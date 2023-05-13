# Philips Hue Lighting System - Event Listener and Logger

This repository is a system for listening to events from a Philips Hue bridge and logging those events
into an influxdb time series database. It captures a wide range of events from the system including
things like lights being turned on and off, motion detection from the motion sensors as well as temperature
and ambient light levels.

The system uses zeroconf to locate the bridge so it's about as easy to use as it can be.

There are also some helper tools to register applications and create configuration files and also
to list information about the bridge and the devices.

You can read about Hue [here](https://www.philips-hue.com/).


## Getting Started

This section describes how to get started with listening for events.

Setup python environment:

    python3 -m venv pyenv
    source pyenv/bin/activate
    pip3 install -r requirements.txt

Register an application and create configuration:

    ./bin/init-application.py <app_name> <app_instance>

This creates a configuration file in the `configs` directory that the other tools can use.

The event listener uses the event stream interface on the bridge. To listen to all events, run
this:

    ./bin/event-listener.py configs/<my-app-config>.yaml

To filter the events so you only see motion and temperature events, run the command like this:

    ./bin/event-listener.py configs/<my-app-config>.yaml motion temperature
  
This checks the 'type' field in the event data for an exact match. If you run the listener for a while
with no filter and you will see the range that's possible.


## Logging Events To InfluxDB

The utility `event-logger.py` can be used with `event-listener.py` to log events to an InfluxDB database.

Information about InfluxDB can be found [here](https://docs.influxdata.com/influxdb/v2.6/get-started/).
To install OpenSource InfluxDB 2.x, follow the instructions on their download portal
[here](https://portal.influxdata.com/downloads/).

The utility `event-logger.py` uses the InfluxData python client library. You can read about
it [here](https://docs.influxdata.com/influxdb/v2.0/api-guide/client-libraries/python/).

To run the event capture with logging, run a command like this:

    export IDB_TOKEN="influxdb-access-token"
    export IDB_ORG="influxdb-org-name"
    export IDB_BUCKET="influxdb-bucket-to-log-to"
    export IDB_URL="http://<your-influxdb-host>:8086"

    ./bin/event-listener.py configs/myconfig.yaml temperature motion light_level | ./bin/event-logger.py

You'll start seeing events arriving in InfluxDB.

The logger currently only logs 'temperature', 'light_level' and 'motion' events. There's no reason why
other events can't be logged, I was just interested in these ones so didn't bother adding support for 
other event types or even better, generalizing the code to handle any event type. On the todo list.


## Helper Utilities

The utilities all use zeroconf technologies to locate your bridge so there's no need to go
hunting around for your bridge IP address. If the phone app can find the bridge on your network,
then these utilities will as well.

Bridge Info: Prints basic information about the bridge.

    ./bin/bridge-info.py

Init Application: Registers an application with the bridge and creates a config file for it.

    ./bin/init-application.py <app_name> <app_instance>

List Devices: Lists devices connected to the bridge:

    ./bin/ls-devices.py config/<my-app-config>.yaml

