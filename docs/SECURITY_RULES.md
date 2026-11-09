# Service-review findings (WBS 7.0)

New scans generate findings from detected TCP services while saving results.
Hosts, services, findings and completed status share one database transaction.
If evaluation or storage fails, partial results roll back and the API records
a failed scan. Reads do not re-run rules. Old scans retain their original results;
run a new scan to apply the current rules.

These findings are review prompts, not confirmed exploitable vulnerabilities.
The engine does not test passwords, authentication, exploitation, CVEs, anonymous
FTP, TLS negotiation, redirects, certificate validity, or Internet exposure.

| Rule | Match | Severity | Review action |
|---|---|---|---|
| HTTP-001 | TCP `http` or `http-proxy` on 80, 3000, 8000, 8008, 8080, 8888 | Low | Verify HTTPS enforcement and redirects before sending sensitive data |
| TELNET-001 | TCP `telnet`, excluding 992 | High | Review legacy remote sessions; prefer SSH and restrict access |
| FTP-001 | TCP `ftp`, excluding 990 | Medium | Verify encrypted transfer and authentication; consider SFTP |
| PRINT-001 | TCP `jetdirect` or `pdl-datastream` on 9100 | Medium | Restrict raw printing to approved clients |
| SSH-001 | TCP `ssh` | Info | Review administrator access; SSH availability is not itself a vulnerability |

Severity is a fixed review priority, not a CVSS score: High prioritizes legacy
remote access; Medium covers transfer/printing policy; Low requests transport
review; Info documents administrative service availability. No current rule
assigns Critical. The API/UI retain all five existing severities.

Rules require a recognized service name; an open conventional port alone is not
enough. Missing, unknown, UDP, or unmatched service observations produce no finding.
The scanner contract currently omits Nmap's TLS tunnel metadata. Consequently the
HTTP rule is restricted to a documented port set and does not classify `http` on
443/8443 as plaintext. Even on port 80 it requests a review rather than asserting
that sensitive information was transmitted without encryption. TLS detection and
certificate evaluation would require a separate interface change and tests.

## Verification

`backend/api/test_rules.py` covers matches and exclusions, TLS false-positive
avoidance, API/history counts, host/service associations, repeat scans, read-only
retrieval, and transaction rollback on a rule error. Existing endpoint tests use
explicit finding fixtures to test query behavior independently. Frontend tests
verify severity filtering, detail rendering, and the limitation text.

The isolated six-target lab should produce 11 findings: 9 Low HTTP reviews,
1 Medium printing review, and 1 Info SSH review. The HTTPS service on .24:443
must not receive HTTP-001. Telnet/FTP rules use test fixtures; those services are
not enabled in this lab. This rule set is on a feature branch for team review.
