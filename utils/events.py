#!/usr/bin/env python3
import argparse
import time
import json
import hlib


def get_devices(cl):
    resp = cl.get("/clip/v2/resource/device")
    if resp.status_code != 200:
        print(f"Request failed with {resp.status_code} {resp.reason}")
        return
    
    data = resp.json()
    raw_devices = data['data']
        
    devices = {}
    
    for d in raw_devices:
        top_id = d['id']
        
        device = {
            'id': top_id,
            'type': d['type'],
            'product': d['product_data']['product_name'],
            'archtype': d['metadata']['archetype'],
            'name': d['metadata']['name'],
        }
        devices[top_id] = device
        
    return devices


def run(config_file, types):
    
    types = set(types)

    bridge = hlib.find_bridge()
    if bridge is None:
        print("Could not locate a bridge")
        return

    cfg = hlib.load_config(config_file)
    cl = hlib.new_client(bridge.address, cfg['user_name'])
    
    # get the devices
    devices = get_devices(cl)
    
    # start listening for events
    headers = {
        "Accept": "text/event-stream"
    }
    
    prefix = "data: "
    resp = cl.get("/eventstream/clip/v2", extra_headers=headers, stream=True, timeout=60)
    for line in resp.iter_lines():
        line = line.decode('utf-8')
        if len(line) == 0:
            continue
            
        if not line.startswith(prefix):
            continue
            
        line = line[len(prefix):]
        events = json.loads(line)
        
        for event in events:
            datas = event['data']
            for data in datas:
                # only report events related to devices
                if data['owner']['rtype'] != 'device':
                    continue

                # filter types
                dtype = data['type']
                if len(types) > 0 and dtype not in types:
                    continue
                
                data['event_stamp'] = event['creationtime']
                data['event_id'] = event['id']
                data['event_type'] = event['type']
                
                owner_id = data['owner']['rid']
                if owner := devices.get(owner_id, None):
                    data['owner'] = owner
                
                jdata = json.dumps(data)
                print(jdata, flush=True)
                
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="configuration file to load", type=str)
    parser.add_argument("types", help="event types to filter for", type=str, nargs='*', default=None)
    args = parser.parse_args()
    
    while True:
        try:
            run(args.config_file, args.types)
        except KeyboardInterrupt:
            break
        except:
            print('{"ping": "ping"}', flush=True)
            time.sleep(60)
            pass


if __name__ == "__main__":
    main()

