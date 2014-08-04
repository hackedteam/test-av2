#!/bin/bash

cd /home/avmonitor/AVTest/AVMaster/

echo "Clean Targets"
sh clean_targets_minotauro.sh
echo "Revert all VMs"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py revert 
echo "Starting VMs"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py command -c start 
sleep 180

echo "Pushing melt"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py push -k melt 
echo "Pushing melt"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py push -k all 
