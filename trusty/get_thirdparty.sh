#!/usr/bin/env bash

links="./thirdparty.urls"
failure=0

platform="trusty"
out_dir="/tmp/packages/${platform}/"

# Fetch Packages
wget -P "${out_dir}" -i "${links}"
if [[ $? -ne 0 ]]
then
    echo "Download failed"
    failure=1
fi

exit ${failure}