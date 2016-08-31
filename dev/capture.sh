#!/bin/sh

# source /usr/local/bin/virtualenvwrapper.sh >> /Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev/logs/pm_error.txt 2>&1 

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/go/bin:/usr/local/sbin:/Users/james/Dropbox/Development/go/bin:/usr/local/mysql/bin"
# ===================== Python ====================================================
export PYTHONPATH=/Users/james/Dropbox/Development/_Tools/PDF/TET/bind/python/python33
# Virtualenvwrapper
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python3
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh


workon cfsj_jailstats >> /Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev/logs/pm_error.txt 2>&1 
if [ "$?" != "0" ]; then
    echo "[Error] workon failed" 2>&1
    exit 1
fi

cd /Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev >> /Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev/logs/pm_error.txt 2>&1 
if [ "$?" != "0" ]; then
    echo "Change directory failed" 2>&1
    exit 1
fi

python /Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev/capture.py -m immediate ptest >> /Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev/logs/pm_error.txt 2>&1 
if [ "$?" != "0" ]; then
    echo "CFSJ JailStat Capture failed!" 2>&1
    exit 1
fi