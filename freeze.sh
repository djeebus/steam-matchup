#!/usr/bin/env bash

PIP_COMPILE=`which pip-compile`
if [ -z $PIP_COMPILE ]; then
    echo 'Must run "pip install pip-tools"'
    exit 1
fi

pip-compile reqs/install.in > reqs/install.txt
echo "Requirements have been updated in reqs/install.txt"