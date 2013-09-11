#!/usr/bin/env bash

packages=( */debian )

for p in "${packages[@]}"
do
    pushd "${p}" > /dev/null
    rm *.deb
    rm *.dsc
    equivs-build -f "control"
    popd > /dev/null
done
