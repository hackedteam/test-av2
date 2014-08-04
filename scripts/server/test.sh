#!/bin/bash

cd /home/avmonitor/AVTest/AVMaster/

echo "Executing tests"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py dispatch -k all -v -m all
