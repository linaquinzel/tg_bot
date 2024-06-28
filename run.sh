#!/bin/bash
set -e
exec python main.py 
exec python mqtt/mqtt.py &
exec python subscriber/subscriber.py &