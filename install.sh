#!/usr/bin/env bash

packages=$(ls | grep "cu-cs-")

for p in ${packages}
do
    pushd "${p}/debian/" > /dev/null
    deb=$(readlink -f *.deb)
    dsc=$(readlink -f *.dsc)
    pushd "/srv/apt/ubuntu/" > /dev/null
    reprepro includedeb precise "${deb}"
    reprepro includedsc precise "${dsc}"
    popd > /dev/null
    popd > /dev/null
done
