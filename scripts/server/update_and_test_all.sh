#!/bin/bash

today=$(date "+%Y%m%d")
echo $today

#echo "Clean Targets"
#cd /home/avmonitor/AVTest/AVAgent
#/usr/bin/python lib/agent.py clean -b rcs-minotauro -f rcs-teseo

rm -fr /home/avmonitor/Rite/logs/*

echo "Updating VMs"
cd /home/avmonitor
sh update.sh -e $today

killall -9 vmrun

echo "Executing tests"
./run.sh SYSTEM_DAILY -c -e $today -p 16

chmod 755 /opt/AVTest2/rite_retest.sh
/opt/AVTest2/rite_retest.sh -p 16

./run.sh SYSTEM_STOP -p 30

./run.sh SYSTEM_FUNCTIONAL_RITE -c -e $today
./run.sh SYSTEM_FUNCTIONAL_SKYPE_RITE -c -e $today
./run.sh SYSTEM_FUNCTIONAL_SOLDIER_RITE -c -e $today

./run.sh SYSTEM_STOP -m funie,funch,funff -c -e $today

#chmod 755 /opt/AVTest2/rite_retest.sh
#/opt/AVTest2/rite_retest.sh

#./run.sh SYSTEM_STOP -p 30
#killall -9 vmrun

