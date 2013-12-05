#!/bin/sh
rm *.log
python av_master.py -r $1 | tee run.log