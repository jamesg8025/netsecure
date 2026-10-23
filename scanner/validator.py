"""
NetSecure Target Validator

This module validates scan targets before they are passed
to Nmap. NetSecure will only allow loopback addresses and
private IPv4 networks that are appropriate for authorized
local network scanning.

Author: Zachary Domingue
"""

import ipaddress


class InvalidTargetError(ValueError):
    pass


def validate_target(target):
    if not isinstance(target, str):
        raise InvalidTargetError("Target must be a valid IPv4 address or CIDR network.")
    target = target.strip()

    try:
        network = ipaddress.ip_network(target, strict=False)
    except ValueError:
        raise InvalidTargetError(
            "Target must be a valid IPv4 address or CIDR network."
        )

    if network.version != 4:
        raise InvalidTargetError(
            "NetSecure currently supports IPv4 targets only."
        )

    # Check the entire range against explicit RFC 1918 and loopback networks.
    allowed = ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8")
    if not any(network.subnet_of(ipaddress.ip_network(item)) for item in allowed):
        raise InvalidTargetError(
            "NetSecure only allows authorized private network targets."
        )

    # Prevent accidentally scanning very large ranges.
    if network.num_addresses > 256:
        raise InvalidTargetError(
            "Target range is too large. Maximum size is 256 addresses."
        )

    return str(network) if "/" in target else str(network.network_address)


def main():
    test_targets = [
        "127.0.0.1",
        "192.168.1.25",
        "192.168.1.0/24",
        "10.0.0.15",
        "8.8.8.8",
        "google.com"
    ]

    print("NetSecure Target Validation Test")
    print("--------------------------------")

    for target in test_targets:
        try:
            validate_target(target)
            print(f"ALLOWED:  {target}")
        except InvalidTargetError as error:
            print(f"REJECTED: {target}")
            print(f"          {error}")


if __name__ == "__main__":
    main()
