#!/bin/bash

cd /home/avmonitor/AVTest/VMAVTest/

echo "Executing tests"
/usr/bin/python lib/vmavtest.py clean -b rcs-minotauro -f rcs-teseo
