#!/usr/bin/env bash

packages=( */debian )
failure=0

platform="trusty"
base_dir="/tmp/cu-cs-pkg-build"
build_dir="${base_dir}/${platform}/"
out_dir="/tmp/packages/${platform}/"

gpgkeys="${HOME}/cu/packages/cu-cs-apt-keys"

# Set GNUPGHOME
old_GNUPGHOME="${GNUPGHOME}"
export GNUPGHOME="${gpgkeys}"

# Setup Dirs
rm -rf "${base_dir}"
git checkout-index -a -f --prefix="${base_dir}/"
mkdir -p "${out_dir}"

# Build
pushd "${build_dir}"
for p in ./*
do
    if [[ -d ${p} ]]
    then
	pushd "${p}/debian/"
	echo "Building ${p}..."
	equivs-build -f "control" > /dev/null
	if [[ $? -ne 0 ]]
	then
	    echo "Build failed"
	    failure=1
	else
	    echo "Build succeeded"
	    mv ${p}_*.deb ${out_dir}
	    mv ${p}_*.dsc ${out_dir}
	    mv ${p}_*.changes ${out_dir}
	    mv ${p}_*.tar.gz ${out_dir}
	fi
	popd
    else
	continue
    fi
done
popd

# Clean Up
rm -rf "${base_dir}"

# Reset GNUPGHOME
if [[ -z "${old_GNUPGHOME}" ]]
then
    unset GNUPGHOME
else
    export GNUPGHOME="${old_GNUPGHOME}"
fi

# Report Errors
if [[ ${failure} -ne 0 ]]
then
    echo "There were build errors..."
fi

exit ${failure}
