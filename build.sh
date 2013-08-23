#!/usr/bin/env bash

packages=$(ls | grep "cu-cs-")

for p in ${packages}
do
    pushd "${p}/debian/" > /dev/null
    equivs-build -f "control"
    popd > /dev/null
done
