#!/bin/sh

# Andy Sayler
# cu-cs-apt-ubuntu Package
# Post-remove Script

list="/etc/apt/sources.list"

sed -i 's/^###//g' "${list}"
if [ $? -ne 0 ]
then
    echo "Failed to enable sources in ${list}"
    exit 1
else
    echo "Enabled sources in ${list}"
    exit 0
fi
