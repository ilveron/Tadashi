#!/usr/bin/bash

if [ $# -eq 1 ] && [ "$1" != "-v" ] || [ $# -gt 1 ]
  then
    echo "Invalid argument, use -v for verbose mode"
    exit 1
fi

./phase_1.py
./phase_2.py 

echo "PHASE 3 - I-DLV-SR ANSWER STREAMS COMPARISON"
if [ "$1" == "-v" ]
  then
    # Running in verbose mode
    ./phase_3.py > tadashi/verbose_report.txt
else
    ./phase_3.py > /dev/null
fi
