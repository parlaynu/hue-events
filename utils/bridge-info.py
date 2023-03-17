#!/usr/bin/env python3
from hlib import find_bridge


def main():
    bridge = find_bridge()
    if bridge is None:
        print("No bridge found")
        return

    print("Bridge:")
    print(f" Hostname: {bridge.hostname}")
    print(f"       ID: {bridge.id}")
    print(f"    Model: {bridge.model_id}")
    print(f"Addresses:", end= "")
    for address in bridge.addresses:
        print(f" {address}", end="")
    print("")


if __name__ == "__main__":
    main()