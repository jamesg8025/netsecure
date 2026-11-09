"""Conservative service-review rules (WBS 7.0, FR-05/FR-06).

These use Nmap observations, not exploit, authentication, or CVE checks.
The scanner contract does not retain Nmap's TLS tunnel field. In particular,
an `http` service on 443 must not be treated as confirmed plaintext HTTP.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RuleMatch:
    rule_id: str
    severity: str
    title: str
    description: str


HTTP_REVIEW_PORTS = frozenset({80, 3000, 8000, 8008, 8080, 8888})


def evaluate_service(*, port, protocol, service_name):
    """Return zero or one review warning for a detected TCP service.

    Require a recognized service name as well as any rule-specific port.
    A conventional port number alone is not proof of its service/protocol.
    """
    name = (service_name or '').strip().lower()
    if (protocol or '').lower() != 'tcp':
        return []
    observation = f'Nmap reported {name} on TCP port {port}. '
    if name in {'http', 'http-proxy'} and port in HTTP_REVIEW_PORTS:
        warning = RuleMatch(
            'HTTP-001', 'low', 'Review HTTP transport protection',
            observation + 'Review HTTPS enforcement and redirects before sending sensitive data. '
            'This rule does not verify TLS, redirect behavior, authentication, or an exploitable vulnerability.',
        )
    elif name == 'telnet' and port != 992:
        warning = RuleMatch(
            'TELNET-001', 'high', 'Review legacy Telnet access',
            observation + 'Telnet commonly uses unencrypted remote sessions. Prefer SSH and restrict '
            'access to trusted administrators. Encryption and login policy were not tested.',
        )
    elif name == 'ftp' and port != 990:
        warning = RuleMatch(
            'FTP-001', 'medium', 'Review FTP transport and access',
            observation + 'Verify encrypted transfer and authentication, or use SFTP. '
            'Anonymous access, TLS negotiation, and file permissions were not tested.',
        )
    elif name in {'jetdirect', 'pdl-datastream'} and port == 9100:
        warning = RuleMatch(
            'PRINT-001', 'medium', 'Restrict raw printing access',
            observation + 'Restrict this printing endpoint to approved clients to reduce unwanted job '
            'submission. Device identity, authentication, and printing behavior were not tested.',
        )
    elif name == 'ssh':
        warning = Warning(
            'SSH-001', 'info', 'Review remote administration access',
            observation + 'Confirm that only approved administrators can reach and sign in to this service. '
            'SSH availability alone is not a vulnerability; credentials and configuration were not tested.',
        )
    else:
        return []
    return [warning]
