#!/bin/bash

DATE=`date +%Y%m%d%H%M`

# preparing header

cat template.csv >> root-$DATE.csv
echo " " >> root-$DATE.csv

for file in `ls tmp/`
do
    cat tmp/$file >> root-$DATE.csv
done

echo "all done"