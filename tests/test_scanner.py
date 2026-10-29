import contextlib
import io
import json
import subprocess
import unittest
from unittest.mock import patch

from scanner import scanner
from scanner.validator import InvalidTargetError, validate_target

XML = '''<nmaprun><host><status state="up"/><address addr="127.0.0.1" addrtype="ipv4"/>
<ports><port protocol="tcp" portid="22"><state state="open"/>
<service name="ssh" product="OpenSSH" version="9"/></port>
<port protocol="tcp" portid="80"><state state="closed"/></port></ports></host>
<host><status state="down"/></host></nmaprun>'''


class ScannerTests(unittest.TestCase):
    def test_allowed_and_normalized_targets(self):
        for target in ("127.0.0.1", "10.0.0.1", "172.16.0.1", "192.168.1.0/24", "127.0.0.0/24"):
            self.assertEqual(validate_target(target), target)
        self.assertEqual(validate_target(" 192.168.1.42/24 "), "192.168.1.0/24")

    def test_rejected_targets_never_start_nmap(self):
        targets = ("8.8.8.8", "google.com", "", "::1", "0.0.0.0", "169.254.1.1",
                   "192.0.2.1", "224.0.0.1", "10.0.0.0/23", "127.0.0.0/8",
                   "192.168.0.0/15", "127.0.0.1; whoami", "-sV", None)
        with patch.object(scanner.subprocess, "run") as run:
            for target in targets:
                for entry in (scanner.run_scan, scanner.scan_target):
                    with self.subTest(target=target, entry=entry.__name__):
                        with self.assertRaises(InvalidTargetError):
                            entry(target)
            run.assert_not_called()

    def test_scan_and_parse(self):
        with patch.object(scanner.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, XML, "")) as run:
            hosts = scanner.scan_target("127.0.0.1")
        self.assertEqual(hosts, [{"ip": "127.0.0.1", "hostname": "", "services": [
            {"port": 22, "protocol": "tcp", "service": "ssh", "product": "OpenSSH", "version": "9"}]}])
        run.assert_called_once_with(["nmap", "-sV", "-oX", "-", "127.0.0.1"], capture_output=True, text=True, timeout=300)

    def test_execution_failures(self):
        for error in (FileNotFoundError(), OSError("denied"), subprocess.TimeoutExpired("nmap", 300)):
            with patch.object(scanner.subprocess, "run", side_effect=error):
                with self.assertRaises(scanner.ScanError):
                    scanner.run_scan("127.0.0.1")
        with patch.object(scanner.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "failed")):
            with self.assertRaises(scanner.ScanError):
                scanner.run_scan("127.0.0.1")

    def test_invalid_xml_and_empty_scan(self):
        for xml in ("bad", "<wrong/>"):
            with self.assertRaises(scanner.ScanError):
                scanner.parse_scan(xml)
        self.assertEqual(scanner.parse_scan("<nmaprun/>"), [])

    def test_missing_output_and_bad_port_raise_scan_error(self):
        for xml in (None, ""):
            with self.assertRaises(scanner.ScanError):
                scanner.parse_scan(xml)
        bad_port = XML.replace(' portid="22"', "")
        with self.assertRaises(scanner.ScanError):
            scanner.parse_scan(bad_port)

    def test_nonzero_exit_message_is_concise(self):
        stderr = "Starting Nmap\nFailed to open device eth0\nQUITTING!\n"
        with patch.object(scanner.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", stderr)):
            with self.assertRaises(scanner.ScanError) as caught:
                scanner.run_scan("127.0.0.1")
        self.assertEqual(str(caught.exception), "Nmap exited with code 1: Failed to open device eth0")

    def test_cli_public_target_is_error_not_empty_success(self):
        with patch.object(scanner.subprocess, "run") as run, contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(scanner.main(["8.8.8.8"]), 2)
        run.assert_not_called()
        self.assertIn("Target rejected", error.getvalue())
        self.assertNotIn("No active hosts", output.getvalue())

    def test_prompt_and_cancel(self):
        with patch("builtins.input", return_value="127.0.0.1"), patch.object(scanner, "scan_target", return_value=[]) as scan:
            self.assertEqual(scanner.main([]), 0)
            scan.assert_called_once_with("127.0.0.1", profile="basic")
        with patch("builtins.input", side_effect=EOFError):
            self.assertEqual(scanner.main([]), 130)

    def test_discovery_profile(self):
        with patch.object(scanner.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, XML, "")) as run:
            scanner.scan_target("127.0.0.1", profile="discovery")
        self.assertEqual(run.call_args.args[0], ["nmap", "-sn", "-oX", "-", "127.0.0.1"])

    def test_profile_cannot_inject_options_or_bypass_validation(self):
        with patch.object(scanner.subprocess, "run") as run:
            with self.assertRaises(scanner.ScanError):
                scanner.run_scan("127.0.0.1", profile="-A")
            with self.assertRaises(InvalidTargetError):
                scanner.run_scan("8.8.8.8", profile="discovery")
            run.assert_not_called()

    def test_json_stdout_is_machine_readable(self):
        expected = scanner.parse_scan(XML)
        with patch.object(scanner, "scan_target", return_value=expected), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(scanner.main(["127.0.0.1", "--json"]), 0)
        self.assertEqual(json.loads(output.getvalue()), expected)

    def test_incomplete_or_invalid_host_data_fails(self):
        invalid = [XML.replace('addr="127.0.0.1"', 'addr="invalid"'),
                   XML.replace('addrtype="ipv4"', 'addrtype="mac"'),
                   XML.replace('portid="22"', 'portid="65536"'),
                   XML.replace('protocol="tcp"', 'protocol="invalid"'),
                   '<nmaprun><runstats><finished exit="error"/></runstats></nmaprun>']
        for xml in invalid:
            with self.subTest(xml=xml), self.assertRaises(scanner.ScanError):
                scanner.parse_scan(xml)

    def test_discovered_host_without_services(self):
        xml = '<nmaprun><host><status state="up"/><address addrtype="ipv4" addr="127.0.0.1"/></host></nmaprun>'
        self.assertEqual(scanner.parse_scan(xml), [{"ip": "127.0.0.1", "hostname": "", "services": []}])

    def test_cli_scan_failure_does_not_print_results(self):
        with patch.object(scanner, "scan_target", side_effect=scanner.ScanError("failed")), contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(scanner.main(["127.0.0.1", "--json"]), 1)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("Scan failed: failed", error.getvalue())


if __name__ == "__main__":
    unittest.main()
