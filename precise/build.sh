#!/usr/bin/env bash

packages=( */debian )
failure=0
build_dir="/tmp/cu-cs-pkg-build/"
platform="precise"

rm -rf "${build_dir}"
git checkout-index -a -f --prefix="${build_dir}"

pushd "${build_dir}"/"${platform}"
if [ $? -ne 0 ]
then
    echo "Failed to open ${build_dir}/${platform}"
    exit 1
fi

for p in "${packages[@]}"
do
    pushd "${p}"
    rm -f *.deb
    rm -f *.dsc
    echo "Building ${p}..."
    equivs-build -f "control" > /dev/null
    if [ $? -ne 0 ]
    then
	echo "Build failed"
	failure=1
    else
	echo "Build succeeded"
    fi
    popd
done

if [ ${failure} -ne 0 ]
then
    echo "There were build errors..."
fi

popd

exit ${failure}
