#!/bin/bash

cd /home/avmonitor/AVTest/AVMaster/

echo "Clean Targets"
/usr/bin/python lib/agent.py clean -b rcs-minotauro -f rcs-teseo
echo "Revert all VMs"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py --pool 8 revert -m all
echo "Updating VMs"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py --pool 8 update  -v -m all
echo "Executing tests"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py --pool 8 dispatch -k all -v -m all