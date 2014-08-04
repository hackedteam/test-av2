#!/bin/bash

cd /home/avmonitor/AVTest/VMAVTest

echo "Clean Targets"
/usr/bin/python lib/vmavtest.py clean -b rcs-minotauro -f rcs-teseo
echo "Revert all VMs"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py revert -m all 
echo "Executing tests"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py dispatch -k all -v -m all
