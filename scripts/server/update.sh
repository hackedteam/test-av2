#!/bin/sh
./run.sh REVERT -p 30 -c $*
./run.sh UPDATE_FULL -p 15 -c $*
./run.sh SYSTEM_POSITIVE -p 15 -c $*

killall vmrun
sleep 10
killall -9 vmrun
