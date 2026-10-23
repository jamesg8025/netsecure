"""
NetSecure Network Scanner

This module will handle Nmap network scanning for NetSecure.
It will eventually discover active hosts, open ports, and
services running on authorized local networks.

Author: Zachary Domingue
"""

import subprocess


def run_scan(target):
    print(f"\nScanning {target}...")
    
    result = subprocess.run(
        ["nmap", target],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("Scan failed.")
        print(result.stderr)


def main():
    print("NetSecure Scanner")
    print("Scanner module initialized successfully.")

    target = "127.0.0.1"
    run_scan(target)


if __name__ == "__main__":
    main()