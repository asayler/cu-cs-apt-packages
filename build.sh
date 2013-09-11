#!/usr/bin/env bash

packages=( */debian )

for p in "${packages[@]}"
do
    pushd "${p}" > /dev/null
    rm -f *.deb
    rm -f *.dsc
    equivs-build -f "control"
    popd > /dev/null
done
