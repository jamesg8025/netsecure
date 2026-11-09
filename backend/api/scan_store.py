"""
Scan storage and dashboard queries (WBS 5.0, FR-03, NFR-04).

Lifecycle, as set out in database/README.md:

    scan = create_scan(target, profile)   # pending, no timestamps
    start_scan(scan)                      # running + started_at
    ... run Nmap OUTSIDE any transaction ...
    save_results(scan, hosts)             # results + completed, one transaction
    # or, on failure:
    fail_scan(scan, message)              # failed + finished_at + error_message

save_results() is database/import_scan.py's import step, adapted to take the
scanner's own result list (docs/SCANNER_HANDOFF.md) instead of a text report,
and to accept a scan that found no hosts.

The query functions return the same rows as database/history_results.sql,
service_results.sql, and finding_results.sql (the tests check this).

Timestamps are UTC, stored to the second (YYYY-MM-DD HH:MM:SS).
"""
from django.db import transaction
from django.db.models import Case, Count, IntegerField, Value, When
from django.utils import timezone

from .models import Finding, Host, Scan, Service
from .rules import evaluate_service


class ScanStateError(Exception):
    """The scan isn't in the state this step needs (e.g. saving results twice)."""


def _now():
    return timezone.now().replace(microsecond=0)


def _blank_to_none(value):
    """The scanner reports missing metadata as ''; the schema stores NULL."""
    return value or None


# --- Lifecycle -------------------------------------------------------------

def create_scan(target, profile=Scan.Profile.BASIC, user=None):
    """Record a requested scan. `target` must already be validated (FR-02)."""
    return Scan.objects.create(target=target, profile=profile, user=user)


def start_scan(scan):
    """Mark a pending scan running and stamp its actual start time."""
    started_at = _now()
    updated = Scan.objects.filter(pk=scan.pk, status=Scan.Status.PENDING).update(
        status=Scan.Status.RUNNING, started_at=started_at)
    if not updated:
        raise ScanStateError(f'Scan {scan.pk} is not pending.')
    scan.status, scan.started_at = Scan.Status.RUNNING, started_at


def save_results(scan, hosts):
    """
    Save hosts, services and rule findings, then complete the scan atomically.

    `hosts` is scan_target()'s return value:
        [{"ip", "hostname", "services": [{"port", "protocol", "service", "product", "version"}]}]
    An empty list is a valid result: the scan completes with zero hosts.
    If anything fails, nothing is saved and the scan stays running.
    Returns (hosts_saved, services_saved).
    """
    with transaction.atomic():
        if Host.objects.filter(scan_id=scan.pk).exists():
            raise ScanStateError(f'Scan {scan.pk} already has results.')

        service_count = 0
        for host in hosts:
            host_row = Host.objects.create(
                scan_id=scan.pk, ip_address=host['ip'], hostname=_blank_to_none(host.get('hostname')))
            services = [
                Service(
                    host=host_row,
                    port=service['port'],
                    protocol=service['protocol'],
                    service_name=_blank_to_none(service.get('service')),
                    product=_blank_to_none(service.get('product')),
                    version=_blank_to_none(service.get('version')),
                )
                for service in host.get('services', [])
            ]
            Service.objects.bulk_create(services)
            # SQLite returns generated service IDs from bulk_create. Findings
            # belong to those exact rows and share the result transaction.
            Finding.objects.bulk_create([
                Finding(
                    service=service_row,
                    severity=warning.severity,
                    title=f'{warning.rule_id}: {warning.title}',
                    description=warning.description,
                )
                for service_row in services
                for warning in evaluate_service(
                    port=service_row.port,
                    protocol=service_row.protocol,
                    service_name=service_row.service_name,
                )
            ])
            service_count += len(services)

        finished_at = _now()
        updated = Scan.objects.filter(pk=scan.pk, status=Scan.Status.RUNNING).update(
            status=Scan.Status.COMPLETED, finished_at=finished_at)
        if not updated:
            raise ScanStateError(f'Scan {scan.pk} is not running.')

    scan.status, scan.finished_at = Scan.Status.COMPLETED, finished_at
    return len(hosts), service_count


def fail_scan(scan, message):
    """Mark a pending or running scan failed and keep the reason (NFR-04)."""
    finished_at = _now()
    message = (message or '').strip() or 'Scan failed.'
    updated = Scan.objects.filter(
        pk=scan.pk, status__in=[Scan.Status.PENDING, Scan.Status.RUNNING],
    ).update(status=Scan.Status.FAILED, finished_at=finished_at, error_message=message)
    if not updated:
        raise ScanStateError(f'Scan {scan.pk} has already finished.')
    scan.status, scan.finished_at, scan.error_message = Scan.Status.FAILED, finished_at, message


# --- Dashboard queries -----------------------------------------------------

STATUS_LABELS = {
    Scan.Status.PENDING: 'Pending',
    Scan.Status.RUNNING: 'In-Progress',
    Scan.Status.COMPLETED: 'Completed',
    Scan.Status.FAILED: 'Failed',
}

SEVERITY_ORDER = ['critical', 'high', 'medium', 'low', 'info']


def scan_history(user=None):
    """
    Scan History rows, newest first (history_results.sql).

    With `user`, only that user's scans. With no user, every scan: that is the
    pre-login behaviour (WBS 9.0). Once login exists, views must pass the
    signed-in user.
    """
    scans = Scan.objects.all()
    if user is not None:
        scans = scans.filter(user=user)
    # distinct=True stops the hosts→findings join inflating the counts.
    scans = scans.annotate(
        devices_found=Count('hosts', distinct=True),
        findings_found=Count('hosts__services__findings', distinct=True),
    ).order_by('-scan_id')
    return [
        {
            'scan_id': scan.scan_id,
            'target': scan.target,
            'profile': scan.profile,
            'timestamp': scan.started_at,
            'finished_at': scan.finished_at,
            'status': STATUS_LABELS[scan.status],
            'error_message': scan.error_message,
            'devices_found': scan.devices_found,
            'findings_found': scan.findings_found,
        }
        for scan in scans
    ]


def scan_devices(scan_id):
    """
    Devices rows for one scan: one per service, plus one per host with no
    services (service_results.sql). The caller must authorize `scan_id`.
    """
    rows = []
    hosts = Host.objects.filter(scan_id=scan_id).order_by('ip_address').prefetch_related('services')
    for host in hosts:
        base = {'host_id': host.host_id, 'ip_address': host.ip_address, 'hostname': host.hostname}
        services = sorted(host.services.all(), key=lambda s: (s.port, s.protocol))
        if not services:
            rows.append({**base, 'service_id': None, 'port': None, 'protocol': None,
                         'service': None, 'product': None, 'version': None})
        for service in services:
            rows.append({**base, 'service_id': service.service_id, 'port': service.port,
                         'protocol': service.protocol, 'service': service.service_name,
                         'product': service.product, 'version': service.version})
    return rows


def scan_findings(scan_id):
    """
    Findings rows for one scan, most severe first (finding_results.sql).
    The caller must authorize `scan_id`.
    """
    rank = Case(
        *[When(severity=severity, then=Value(i)) for i, severity in enumerate(SEVERITY_ORDER)],
        output_field=IntegerField(),
    )
    findings = (
        Finding.objects.filter(service__host__scan_id=scan_id)
        .select_related('service__host')
        .order_by(rank, 'service__host__ip_address', 'service__port')
    )
    return [
        {
            'finding_id': finding.finding_id,
            'severity': finding.severity,
            'finding': finding.title if finding.title is not None else 'Untitled finding',
            'host': finding.service.host.ip_address,
            'port': finding.service.port,
            'protocol': finding.service.protocol,
            'service': finding.service.service_name,
            'description': finding.description,
        }
        for finding in findings
    ]
