# Utilities for Philips Hue Lighting System

This repository has a few utilities written in python to interact with a Hue lighting system. It
needs a system with a Bridge.

You can read about Hue [here](https://www.philips-hue.com/).

## Getting Started

Setup python environment:

    python3 -m venv pyenv
    source pyenv/bin/activate
    pip3 install -r requirements.txt

Register an application and create configuration:

    ./utils/init-application.py <app_name> <app_instance>

This creates a configuration file in the `configs` directory that the other utilities can use.

To list all the devices on your bridge:

    ./utils/ls-devices.py configs/<my-app-config>.yaml

## Basic Utilities

The utilities all use zeroconf technologies to locate your bridge so there's no need to go
hunting around for your bridge IP address. If the phone app can find the bridge on your network,
then these utilities will as well.

Bridge Info: Prints basic information about the bridge.

    ./utils/bridge-info.py

Init Application: Registers an application with the bridge and creates a config file for it.

    ./utils/init-application.py <app_name> <app_instance>

List Devices: Lists devices connected to the bridge:

    ./utils/ls-devices.py config/<my-app-config>.yaml

## Catching Events

There is a utility to listen on the event stream of the bridge. To report all events on devices, you can 
use it like this.

    ./utils/events.py configs/<my-app-config>.yaml

To report a subset of events, for example 'temperature' and 'motion', run it like this:

    ./utils/events.py configs/<my-app-config>.yaml temperature motion

## Logging Events To InfluxDB

The utility `event-logger.py` can be used with `events.py` to log events to an InfluxDB database.
Information about InfluxDB can be found [here](https://docs.influxdata.com/influxdb/v2.6/get-started/).

To install OpenSource InfluxDB 2.x, follow the instructions on their download portal
[here](https://portal.influxdata.com/downloads/).

The utility `events-logger.py` uses the InfluxData python client library. You can read about
it [here](https://docs.influxdata.com/influxdb/v2.0/api-guide/client-libraries/python/).

To run the event capture with logging, run a command like this:

    export IDB_TOKEN="influxdb-access-token"
    export IDB_ORG="influxdb-org-name"
    export IDB_BUCKET="influxdb-bucket-to-log-to"
    export IDB_URL="http://<your-influxdb-host>:8086"
    
    ./utils/events.py configs/myconfig.yaml temperature motion light_level | ./utils/event-logger.py

You'll start seeing events arriving in InfluxDB.

The logger currently only logs 'temperature', 'light_level' and 'motion' events.

