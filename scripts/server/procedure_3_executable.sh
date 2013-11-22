#!/bin/bash

cd /home/avmonitor/AVTest/AVMaster/

echo "Clean Targets"
sh clean_targets_minotauro.sh
echo "Revert all VMs"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py revert 

echo "Starting VMs"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py command -c start  

sleep 600

echo "Pushing exploit"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py push -k exploit 
