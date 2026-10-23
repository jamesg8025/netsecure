"""
NetSecure Network Scanner

This module handles Nmap network scanning for NetSecure.
It discovers active hosts, open ports, and services running
on authorized local networks.

Author: Zachary Domingue
"""

import subprocess
import xml.etree.ElementTree as ET


def run_scan(target):
    print(f"\nScanning {target}...")

    result = subprocess.run(
        ["nmap", "-sV", "-oX", "-", target],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return result.stdout
    else:
        print("Scan failed.")
        print(result.stderr)
        return None


def parse_scan(xml_output):
    if xml_output is None:
        return []

    root = ET.fromstring(xml_output)

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
                    "port": int(port.get("portid")),
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


def main():
    print("NetSecure Scanner")
    print("Scanner module initialized successfully.")

    target = "127.0.0.1"

    xml_output = run_scan(target)
    hosts = parse_scan(xml_output)
    display_results(hosts)


if __name__ == "__main__":
    main()