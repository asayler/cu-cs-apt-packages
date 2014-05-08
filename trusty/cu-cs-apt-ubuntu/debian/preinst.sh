#!/bin/sh

# Andy Sayler
# cu-cs-apt-ubuntu Package
# Pre-install Script

list="/etc/apt/sources.list"

sed -i 's/^\(deb\)/###\1/g' "${list}"
if [ $? -ne 0 ]
then
    echo "Failed to disable sources in ${list}"
    exit 1
else
    echo "Disabled sources in ${list}"
    exit 0
fi
