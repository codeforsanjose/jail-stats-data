#!/bin/sh
echo "------START------" 
cd /_capture
python capture.py -m immediate test
echo "------END--------"