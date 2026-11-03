"""
Scan result storage (WBS 5.0, FR-03).

These models mirror database/schema.sql (Matt's design): the same table and
column names and the same constraints, so the queries in database/*.sql run
unchanged against Django's database. Django migrations own the schema; don't
also run schema.sql against this database.

One difference: the schema's `users` table is replaced by Django's own user
model (settings.AUTH_USER_MODEL), so there is one login store. A scan's owner
is optional until login exists (WBS 9.0).

Timestamps are UTC and stored to the second (see api.scan_store).
"""
from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Length, Trim
from django.db.models.lookups import GreaterThan


def _not_blank(field):
    """CHECK (length(trim(field)) > 0)"""
    return GreaterThan(Length(Trim(field)), 0)


class Scan(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending'
        RUNNING = 'running'
        COMPLETED = 'completed'
        FAILED = 'failed'

    class Profile(models.TextChoices):
        BASIC = 'basic'
        DISCOVERY = 'discovery'

    scan_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.PROTECT, related_name='scans',
    )
    target = models.TextField()
    profile = models.TextField(choices=Profile.choices, db_default=Profile.BASIC)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.TextField(choices=Status.choices, db_default=Status.PENDING)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'scans'
        indexes = [models.Index(fields=['user', 'scan_id'], name='scans_user')]
        constraints = [
            models.CheckConstraint(condition=_not_blank('target'), name='scans_target_not_blank'),
            models.CheckConstraint(
                condition=Q(profile__in=['basic', 'discovery']), name='scans_profile_valid'),
            models.CheckConstraint(
                condition=Q(status__in=['pending', 'running', 'completed', 'failed']),
                name='scans_status_valid'),
            models.CheckConstraint(
                condition=(
                    Q(status='pending', started_at__isnull=True, finished_at__isnull=True)
                    | Q(status='running', started_at__isnull=False, finished_at__isnull=True)
                    | Q(status='completed', started_at__isnull=False, finished_at__isnull=False)
                    | Q(status='failed', finished_at__isnull=False)
                ),
                name='scans_lifecycle_timestamps',
            ),
            models.CheckConstraint(
                condition=(
                    Q(finished_at__isnull=True) | Q(started_at__isnull=True)
                    | Q(finished_at__gte=F('started_at'))
                ),
                name='scans_finished_after_started',
            ),
            models.CheckConstraint(
                condition=~Q(status='failed') | (Q(error_message__isnull=False) & Q(_not_blank('error_message'))),
                name='scans_failed_has_error',
            ),
            models.CheckConstraint(
                condition=Q(status='failed') | Q(error_message__isnull=True),
                name='scans_error_only_when_failed',
            ),
        ]

    def __str__(self):
        return f'Scan {self.scan_id} ({self.target}, {self.status})'


class Host(models.Model):
    """A device found by one scan; repeated scans keep separate rows (history)."""

    host_id = models.AutoField(primary_key=True)
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, related_name='hosts')
    ip_address = models.TextField()
    hostname = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'hosts'
        constraints = [
            models.UniqueConstraint(fields=['scan', 'ip_address'], name='hosts_one_ip_per_scan'),
            models.CheckConstraint(condition=_not_blank('ip_address'), name='hosts_ip_not_blank'),
        ]

    def __str__(self):
        return self.ip_address


class Service(models.Model):
    """An open TCP/UDP port on a host."""

    class Protocol(models.TextChoices):
        TCP = 'tcp'
        UDP = 'udp'

    service_id = models.AutoField(primary_key=True)
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='services')
    port = models.PositiveIntegerField()
    protocol = models.TextField(choices=Protocol.choices)
    service_name = models.TextField(null=True, blank=True)
    product = models.TextField(null=True, blank=True)
    version = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'services'
        constraints = [
            models.UniqueConstraint(
                fields=['host', 'port', 'protocol'], name='services_one_per_port_protocol'),
            models.CheckConstraint(condition=Q(port__lte=65535), name='services_port_range'),
            models.CheckConstraint(
                condition=Q(protocol__in=['tcp', 'udp']), name='services_protocol_valid'),
        ]

    def __str__(self):
        return f'{self.port}/{self.protocol}'


class Finding(models.Model):
    """A security warning attached to a service (FR-05, FR-06)."""

    class Severity(models.TextChoices):
        INFO = 'info'
        LOW = 'low'
        MEDIUM = 'medium'
        HIGH = 'high'
        CRITICAL = 'critical'

    finding_id = models.AutoField(primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='findings')
    severity = models.TextField(choices=Severity.choices)
    title = models.TextField(null=True, blank=True)
    description = models.TextField()

    class Meta:
        db_table = 'findings'
        constraints = [
            models.CheckConstraint(
                condition=Q(severity__in=['info', 'low', 'medium', 'high', 'critical']),
                name='findings_severity_valid'),
            models.CheckConstraint(
                condition=_not_blank('description'), name='findings_description_not_blank'),
        ]

    def __str__(self):
        return f'{self.severity}: {self.title or self.description[:40]}'
