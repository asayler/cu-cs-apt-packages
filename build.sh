#!/usr/bin/env bash

packages=( */debian )
failure=0

for p in "${packages[@]}"
do
    pushd "${p}" > /dev/null
    rm -f *.deb
    rm -f *.dsc
    echo "Building ${p}..."
    equivs-build -f "control" > /dev/null
    if [$? -ne 0]
    then
	echo "Build failed"
	failure=1
    else
	echo "Build succeeded"
    fi
    popd > /dev/null
done

exit ${failure}
