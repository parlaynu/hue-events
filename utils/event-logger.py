#!/usr/bin/env python3
import sys, os
import select
import time
import json
from pprint import pprint

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


def reader():
    while True:
        rready, _, _ = select.select([sys.stdin,], [], [], 360.0)
        if rready:
            item = sys.stdin.readline()
            yield item.strip()
        else:
            yield '{"ping": "pong"}'


def fromjson(inp):
    for item in inp:
        jdata = json.loads(item)
        jdata['source'] = "live"
        yield jdata


def cacher(inp):
    cache = {}
    
    for item in inp:
        now = time.time()

        # if it's a valid item, cache it and yield it
        if iid := item.get('id', None):
            cache[iid] = (now, item)
            yield item

        # check the cache for older items
        for k, v in cache.items():
            stamp = v[0]   # timestamp with this item was added to the cache
            citem = v[1]   # the cached item
            if now - stamp > 30:  # if more than 5 minutes has elapsed, yield it again
                cache[k] = (now, citem)
                citem['source'] = "cache"
                yield citem


def logger(inp):
    token = os.getenv("IDB_TOKEN")
    org = os.getenv("IDB_ORG")
    bucket = os.getenv("IDB_BUCKET")
    url = os.getenv("IDB_URL")

    client = influxdb_client.InfluxDBClient(
       url=url,
       token=token,
       org=org
    )
    writer = client.write_api(write_options=SYNCHRONOUS)
    
    for item in inp:
        if light := item.get("light", None):
            if light['light_level_valid']:
                record = influxdb_client.Point("light_level")    \
                                    .tag("device", item['id'])  \
                                    .tag("product", item['owner']['product']) \
                                    .tag("name", item['owner']['name'])       \
                                    .field("light_level", light['light_level'])
            
                writer.write(bucket=bucket, org=org, record=record)

        elif motion := item.get("motion", None):
            if motion['motion_valid']:
                value = 1 if motion['motion'] else 0
                record = influxdb_client.Point("motion")          \
                                    .tag("device", item['id'])  \
                                    .tag("product", item['owner']['product']) \
                                    .tag("name", item['owner']['name'])       \
                                    .field("motion", value)
            
                writer.write(bucket=bucket, org=org, record=record)

        elif temp := item.get("temperature", None):
            if temp['temperature_valid']:
                record = influxdb_client.Point("temperature")        \
                                    .tag("device", item['id'])  \
                                    .tag("product", item['owner']['product']) \
                                    .tag("name", item['owner']['name'])       \
                                    .field("temperature", temp['temperature'])
                
                writer.write(bucket=bucket, org=org, record=record)
        
        yield item


def main():
    pipe = reader()
    pipe = fromjson(pipe)
    pipe = cacher(pipe)
    pipe = logger(pipe)
    
    for item in pipe:
        if light := item.get("light", None):
            print(f"{item['source']:>5}: valid: {light['light_level_valid']}, light_level: {light['light_level']},", \
                        f"device: {item['id']}, name: {item['owner']['name']}")
        elif motion := item.get("motion", None):
            print(f"{item['source']:>5}: valid: {motion['motion_valid']}, motion: {motion['motion']},", \
                        f"device: {item['id']}, name: {item['owner']['name']}")
        elif temp := item.get("temperature", None):
            print(f"{item['source']:>5}: valid: {temp['temperature_valid']}, temperature: {temp['temperature']},", \
                        f"device: {item['id']}, name: {item['owner']['name']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass



