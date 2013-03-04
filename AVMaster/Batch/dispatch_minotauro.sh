#!/bin/bash

cd /home/avmonitor/AVTest/AVMaster/

echo "Executing tests"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py --pool 8 dispatch -k scout -v -m all