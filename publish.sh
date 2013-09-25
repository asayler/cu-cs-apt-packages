#!/usr/bin/env bash

packages=( */debian )
failure=0
build_dir="/tmp/cu-cs-pkg-build/"

pushd "${build_dir}"

for p in "${packages[@]}"
do

    pushd "${p}" > /dev/null

    deb_path=$(readlink -f *.deb)
    dsc_path=$(readlink -f *.dsc)
    deb_file=${deb_path##*/}
    deb_name=${deb_file%.*}
    pkg_base=$(echo "${deb_name}" | cut -d _ -f 1) 
    pkg_vers=$(echo "${deb_name}" | cut -d _ -f 2)
    pkg_arch=$(echo "${deb_name}" | cut -d _ -f 3)

    pushd "/srv/apt/ubuntu/" > /dev/null
    echo "Publishing ${pkg_base}"

    rep_vers=$(reprepro list precise | grep "${pkg_base} " | grep amd64 | cut -d ' ' -f 3)

    if [ "${pkg_vers}" != "${rep_vers}" ]
    then
	echo "Version not in repo, adding"
	reprepro -s includedeb precise "${deb_path}" > /dev/null
	if [ $? -ne 0 ]
	then
	    echo "deb publishing failed"
	    failure=1
	else
	    echo "deb publishing succeeded"
	fi
	reprepro includedsc precise "${dsc_path}" > /dev/null
	if [ $? -ne 0 ]
	then
	    echo "dsc publishing failed"
	    failure=1
	else
	    echo "dsc publishing succeeded"
	fi
    else
	echo "Version already in repo, skipping"
    fi
    
    popd > /dev/null
    popd > /dev/null

done

if [ ${failure} -ne 0 ]
then
    echo "There were build errors..."
fi

popd

exit ${failure}
