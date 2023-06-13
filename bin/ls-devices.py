#!/usr/bin/env python3
import argparse
from pprint import pprint

import hlib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', help='configuration file to load', type=str)
    args = parser.parse_args()
    
    bridge = hlib.find_bridge()
    if bridge is None:
        print("Error: failed to locate a bridge")
        return
    
    cfg = hlib.load_config(args.config_file)
    cl = hlib.new_client(bridge, cfg['user_name'])
    
    resp = cl.get("/clip/v2/resource/device")
    if resp.status_code != 200:
        print(f"Request failed with {resp.status_code} {resp.reason}")
        return
    
    data = resp.json()
    devices = data['data']
    
    for idx, device in enumerate(devices):
        if idx > 0:
            print("")
        print(f" Product: {device['product_data']['product_name']}")
        print(f"    Name: {device['metadata']['name']}")
        print(f"      ID: {device['id']}")
        
        services = { svc['rtype'] for svc in device['services'] }
        services = list(services)
        services.sort()
        print("Services:", end="")
        for service in services:
            print(f" {service}", end="")
        print("")

if __name__ == "__main__":
    main()

