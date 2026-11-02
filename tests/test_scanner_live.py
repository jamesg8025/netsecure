"""Opt-in smoke tests: only scan the machine executing these tests."""
import os
import unittest

from scanner.scanner import scan_target


@unittest.skipUnless(os.environ.get("NETSECURE_LIVE_TESTS") == "1", "Set NETSECURE_LIVE_TESTS=1 to scan localhost with Nmap")
class LocalhostScanTests(unittest.TestCase):
    def check_profile(self, profile):
        hosts = scan_target("127.0.0.1", profile=profile)
        self.assertTrue(hosts, "Nmap did not discover localhost")
        self.assertTrue(all(host["ip"] == "127.0.0.1" for host in hosts))
        self.assertTrue(all(isinstance(host["services"], list) for host in hosts))
        return hosts

    def test_basic_profile(self):
        hosts = self.check_profile("basic")
        expected_port = os.environ.get("NETSECURE_LIVE_EXPECT_PORT")
        if expected_port:
            ports = {service["port"] for host in hosts for service in host["services"]}
            self.assertIn(int(expected_port), ports)

    def test_discovery_profile(self):
        self.assertTrue(all(not host["services"] for host in self.check_profile("discovery")))
