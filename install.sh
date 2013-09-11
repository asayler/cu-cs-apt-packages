#!/usr/bin/env bash

packages=( */debian )
failure=0

for p in "${packages[@]}"
do
    pushd "${p}" > /dev/null
    deb=$(readlink -f *.deb)
    dsc=$(readlink -f *.dsc)
    pushd "/srv/apt/ubuntu/" > /dev/null
    echo "Publishing ${deb}..."
    reprepro includedeb precise "${deb}" > /dev/null
    if [ $? -ne 0 ]
    then
	echo "deb publishing failed"
	failure=1
    else
	echo "deb publishing succeeded"
    fi
    echo "Publishing ${dsc}..."
    reprepro includedsc precise "${dsc}" > /dev/null
    if [ $? -ne 0 ]
    then
	echo "dsc publishing failed"
	failure=1
    else
	echo "dsc publishing succeeded"
    fi    
    popd > /dev/null
    popd > /dev/null
done

if [ ${failure} -ne 0 ]
then
    echo "There were build errors..."
fi

exit ${failure}
