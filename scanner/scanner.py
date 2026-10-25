"""
NetSecure Network Scanner

This module handles Nmap network scanning for NetSecure.
It discovers active hosts, open ports, and services running
on authorized local networks.

Author: Zachary Domingue
"""

import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET

if __package__:
    from .validator import validate_target, InvalidTargetError
else:
    from validator import validate_target, InvalidTargetError


class ScanError(RuntimeError):
    """Nmap execution or output could not be processed."""


def run_scan(target):
    target = validate_target(target)
    print(f"\nScanning {target}...")

    try:
        result = subprocess.run(
            ["nmap", "-sV", "-oX", "-", target],
            capture_output=True,
            text=True,
            timeout=300
        )
    except FileNotFoundError as error:
        raise ScanError("Nmap was not found. Install Nmap and add it to PATH.") from error
    except subprocess.TimeoutExpired as error:
        raise ScanError("Nmap exceeded the 300-second scan limit.") from error
    except OSError as error:
        raise ScanError(f"Could not start Nmap: {error}") from error

    if result.returncode == 0:
        return result.stdout

    raise ScanError(_nmap_error_message(result))


def _nmap_error_message(result):
    # Nmap ends fatal errors with "QUITTING!"; the line before it explains why.
    lines = [line.strip() for line in result.stderr.splitlines() if line.strip()]
    lines = [line for line in lines if line != "QUITTING!"]
    if not lines:
        return f"Nmap exited with code {result.returncode}."
    return f"Nmap exited with code {result.returncode}: {lines[-1][:200]}"


def parse_scan(xml_output):
    if not xml_output:
        raise ScanError("Nmap produced no output.")

    try:
        root = ET.fromstring(xml_output)
    except ET.ParseError as error:
        raise ScanError("Nmap returned invalid XML.") from error
    if root.tag != "nmaprun":
        raise ScanError("Nmap output is missing its nmaprun root.")

    hosts = []

    for host in root.findall("host"):
        status = host.find("status")

        if status is None or status.get("state") != "up":
            continue

        ip_address = "Unknown"

        for address in host.findall("address"):
            if address.get("addrtype") == "ipv4":
                ip_address = address.get("addr")

        hostname = ""

        hostname_element = host.find("hostnames/hostname")

        if hostname_element is not None:
            hostname = hostname_element.get("name", "")

        services = []

        for port in host.findall("ports/port"):
            state = port.find("state")

            if state is None or state.get("state") != "open":
                continue

            try:
                port_number = int(port.get("portid"))
            except (TypeError, ValueError) as error:
                raise ScanError("Nmap output contains a port without a valid portid.") from error

            service = port.find("service")

            service_name = ""
            product = ""
            version = ""

            if service is not None:
                service_name = service.get("name", "")
                product = service.get("product", "")
                version = service.get("version", "")

            services.append(
                {
                    "port": port_number,
                    "protocol": port.get("protocol"),
                    "service": service_name,
                    "product": product,
                    "version": version
                }
            )

        hosts.append(
            {
                "ip": ip_address,
                "hostname": hostname,
                "services": services
            }
        )

    return hosts


def display_results(hosts):
    print("\nNetSecure Scan Results")
    print("----------------------")

    if not hosts:
        print("No active hosts were found.")
        return

    for host in hosts:
        print(f"\nIP Address: {host['ip']}")

        if host["hostname"]:
            print(f"Hostname: {host['hostname']}")

        if not host["services"]:
            print("No open services detected.")
            continue

        print("Open Services:")

        for service in host["services"]:
            print(
                f"  Port {service['port']}/{service['protocol']} "
                f"- {service['service']}"
            )

            if service["product"]:
                print(f"    Product: {service['product']}")

            if service["version"]:
                print(f"    Version: {service['version']}")


def scan_target(target):
    xml_output = run_scan(target)
    hosts = parse_scan(xml_output)

    return hosts


def main(argv=None):
    parser = argparse.ArgumentParser(description="Scan an authorized private IPv4 address or subnet (maximum 256 addresses).")
    parser.add_argument("target", nargs="?", help="Private IPv4 address or CIDR; omitted targets are prompted for")
    args = parser.parse_args(argv)
    print("NetSecure Scanner")
    print("Scanner module initialized successfully.")

    try:
        target = args.target if args.target is not None else input("Authorized IPv4 address or subnet: ")
        hosts = scan_target(target)
    except InvalidTargetError as error:
        print(f"Target rejected: {error}", file=sys.stderr)
        return 2
    except ScanError as error:
        print(f"Scan failed: {error}", file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nScan cancelled.", file=sys.stderr)
        return 130
    display_results(hosts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
