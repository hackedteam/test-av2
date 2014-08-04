#!/bin/bash

echo "Clean Targets"
sh clean_targets_minotauro.sh

cd /home/avmonitor/AVTest/AVMaster/

echo "Revert all VMs"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py revert
echo "Starting VMs"
/usr/bin/python /home/avmonitor/AVTest/AVMaster/master.py command -c start
