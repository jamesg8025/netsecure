# Scanner handoff — Zach

## Delivery scope

WBS 3.0 is implemented: Nmap configuration, private IPv4 target validation,
host discovery, port/service detection, and structured XML parsing. This handoff
covers the scanner component, its tests, and its usage documentation. It does
not claim completion of authentication, persistence, API routes, the dashboard,
or whole-system testing owned jointly or by other team members.

## Integration contract

Run Python from the repository root, or place that root on the backend's import
path. Import the package rather than modifying the scanner's own imports:

```python
from scanner.scanner import ScanError, scan_target
from scanner.validator import InvalidTargetError

try:
    hosts = scan_target("127.0.0.1", profile="basic")
except InvalidTargetError as error:
    # Return a validation error to the caller; no Nmap process was started.
    raise
except ScanError as error:
    # Mark the job failed and persist its target, timestamp, and reason.
    raise
```

`scan_target` is synchronous and may take up to the 300-second subprocess timeout.
The backend should execute it in its chosen background job mechanism. A timeout
terminates Nmap and reports failure; incomplete results are not returned.

Illustrative result (synthetic, not evidence from a real device):

```json
[
  {
    "ip": "127.0.0.1",
    "hostname": "localhost",
    "services": [
      {"port": 22, "protocol": "tcp", "service": "ssh", "product": "OpenSSH", "version": "9"}
    ]
  }
]
```

- Only hosts reported up and ports reported open are included.
- `services` may be empty; missing service metadata is an empty string.
- `discovery` reports hosts with empty service lists.
- No active hosts is `[]`; execution and malformed-output failures are exceptions.
- The backend supplies the scan ID, timestamp, owner, job status, and persistence.
- The earlier architecture example used a `hosts` wrapper and `ports` naming.
  The adapter must use the actual list/`services` contract above; this change does
  not silently rename fields or modify another component.

## Verification

On October 29, 2026, all 17 tests passed on Windows with Nmap 7.992. This includes
15 offline regression tests and two real localhost scans (basic and discovery).
The original basic scan discovered localhost and five open TCP services.
The test suite checks public/oversized/IPv6/hostname/injection-like input rejection,
fixed profile selection, missing Nmap, process errors, timeout, malformed XML,
invalid host/port data, filtering, JSON output, and CLI exit behavior.

`.github/workflows/scanner.yml` repeats regression and real localhost checks on
Ubuntu 24.04. Check that workflow's result before claiming Ubuntu compatibility.
Windows WSL was unavailable during local verification. A shared Ubuntu VM and
authorized multi-host subnet demonstration remain team acceptance work.

## Demo commands

```text
python -m unittest discover -s tests -v
python scanner/scanner.py 8.8.8.8
python scanner/scanner.py 127.0.0.1 --profile discovery
python scanner/scanner.py 127.0.0.1 --json
```

The public target command must exit 2 without scanning. The remaining live
commands must exit 0. Demonstrate a team-approved private subnet only after
confirming permission; the implementation caps ranges at 256 addresses.

## Team follow-up

James/Austin: agree the adapter, job execution, and failure logging; enforce
authenticated access and approved targets. Matt: persist the contract above.
Izaiah: render hosts/services and clear job failures. Zach/Austin: jointly review
security warning rules when the rule engine is ready; an open service alone is
not proof of compromise. Zach/James: coordinate the shared VM demo and final
project report after integration. No teammate-owned implementation is changed.
