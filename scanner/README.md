# NetSecure scanner

Run from the repository root with Python 3 and Nmap installed on PATH:

```powershell
python scanner/scanner.py 127.0.0.1
python -m scanner.scanner 192.168.1.0/24
python scanner/scanner.py
python scanner/scanner.py 127.0.0.1 --profile discovery
python scanner/scanner.py 127.0.0.1 --json
```

The last command prompts for a target. Only scan networks you have permission
to test. Private addressing alone does not establish permission.

Targets must be IPv4 literals or CIDRs wholly inside RFC 1918 or loopback space,
with at most 256 addresses. CIDRs with host bits are normalized to the containing
network. Public, reserved, link-local, multicast, hostname and IPv6 targets are
rejected before any subprocess starts, including direct calls to `run_scan`.

The default `basic` profile runs Nmap service detection (`-sV`); `discovery`
runs host discovery only (`-sn`). Both use XML output and a 300-second timeout.
Profiles are fixed argument lists; callers cannot supply arbitrary Nmap options.
The basic profile uses Nmap's default port selection (not every possible port).
Exit codes: 0 success, 1 scan failure, 2 invalid target,
130 cancellation. Scan failures are not reported as successful empty scans.

`scan_target(target, profile="basic")` returns a list of host dictionaries with `ip`, `hostname`,
and `services`. Each service contains `port`, `protocol`, `service`, `product`,
and `version`. Invalid input raises `InvalidTargetError`; execution/output
failures raise `ScanError`. Backend callers should handle these explicitly.
`profile` is keyword-only and defaults to `basic`, so existing callers keep
working. `run_scan` returns XML; `parse_scan` parses XML without running Nmap.
Library functions do not print scan results. With `--json`, stdout contains only
the result list, while banners and errors go to stderr. An empty list means a
successful scan with no discovered hosts; failures raise exceptions instead.

The provisional architecture contract differs; team integration remains pending.
Use this actual contract when writing the adapter, or agree on a versioned change
with the scanner owner. See `docs/SCANNER_HANDOFF.md` for an example and checklist.

Offline tests (no network scans):

```powershell
python -m unittest discover -s tests -v
```

Opt-in live checks scan only `127.0.0.1` on the test machine:

```powershell
$env:NETSECURE_LIVE_TESTS = "1"
python -m unittest discover -s tests -v
```

On Ubuntu: `NETSECURE_LIVE_TESTS=1 python3 -m unittest discover -s tests -v`.
The scanner workflow runs these on Ubuntu 24.04. The scanner requires only the
Python standard library and the external Nmap executable; Django is not needed.
On Windows install Nmap/Npcap and ensure `nmap --version` works in the same shell.
On Ubuntu install with `sudo apt install nmap`. No elevated Python process is
required for the basic profile; Nmap selects a scan method based on privileges.

The API layer must enforce user authentication, approved network permissions,
job scheduling, persistence, and failure logging. This component validates
address syntax/ranges, but does not establish the user's authority to scan them.
