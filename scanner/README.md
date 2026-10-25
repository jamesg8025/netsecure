# NetSecure scanner

Run from the repository root with Python 3 and Nmap installed on PATH:

```powershell
python scanner/scanner.py 127.0.0.1
python -m scanner.scanner 192.168.1.0/24
python scanner/scanner.py
```

The last command prompts for a target. Only scan networks you have permission
to test. Private addressing alone does not establish permission.

Targets must be IPv4 literals or CIDRs wholly inside RFC 1918 or loopback space,
with at most 256 addresses. CIDRs with host bits are normalized to the containing
network. Public, reserved, link-local, multicast, hostname and IPv6 targets are
rejected before any subprocess starts, including direct calls to `run_scan`.

The current profile runs Nmap service detection (`-sV`) with XML output and a
300-second timeout. Exit codes: 0 success, 1 scan failure, 2 invalid target,
130 cancellation. Scan failures are not reported as successful empty scans.

`scan_target(target)` returns a list of host dictionaries with `ip`, `hostname`,
and `services`. Each service contains `port`, `protocol`, `service`, `product`,
and `version`. Invalid input raises `InvalidTargetError`; execution/output
failures raise `ScanError`. Backend callers should handle these explicitly.
The provisional architecture contract differs; team integration remains pending.

Offline tests (no network scans):

```powershell
python -m unittest discover -s tests -v
```
