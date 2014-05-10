#!/usr/bin/env bash

failure=0

platform="trusty"
out_dir="/tmp/packages/${platform}/"
repo_dir="/srv/apt/ubuntu/"

gpgkeys="${HOME}/cu/packages/cu-cs-apt-keys"

# Set GNUPGHOME
old_GNUPGHOME="${GNUPGHOME}"
export GNUPGHOME="${gpgkeys}"

# Enter out directory
pushd "${out_dir}"
if [ $? -ne 0 ]
then
    echo "Failed to open ${out_dir}"
    exit 1
fi

# Process debs
for deb in *.deb
do

    echo "Publishing ${deb}..."

    # Get package info
    pkg_base=${deb%_*}
    pkg_path=$(readlink -f "${deb}")
    pkg_name=$(dpkg -f "${deb}" 'Package')
    pkg_vers=$(dpkg -f "${deb}" 'Version')
    pkg_arch=$(dpkg -f "${deb}" 'Architecture')
    echo "pkg_base = ${pkg_base}"
    echo "pkg_path = ${pkg_path}"
    echo "pkg_name = ${pkg_name}"
    echo "pkg_arch = ${pkg_arch}"
    echo "pkg_vers = ${pkg_vers}"

    # Check for source
    dsc="${pkg_base}.dsc"
    if [[ -f "${dsc}" ]]
    then
	src_path=$(readlink -f "${dsc}")
    else
	src_path=""
    fi
    echo "src_path = ${src_path}"

    # Enter repo directory
    pushd "${repo_dir}"
    if [ $? -ne 0 ]
    then
	echo "Failed to open ${repo_dir}"
	failure=1
	continue
    fi

    # Check repo version
    if [[ "${pkg_arch}" == 'all' ]]
    then
	rep_vers_x64=$(reprepro -T 'deb' -A "amd64" --list-format '${version}' \
	               list "${platform}" "${pkg_name}")
	rep_vers_x32=$(reprepro -T 'deb' -A "i386" --list-format '${version}' \
	               list "${platform}" "${pkg_name}")
	if [[ "${rep_vers_x64}" != "${rep_vers_x32}" ]]
	then
	    echo "All arch version mismatch"
	    rep_vers="${rep_vers_x64}"
	    failure=1
	else
	    rep_vers="${rep_vers_x64}"
	fi
    else
	rep_vers=$(reprepro -T 'deb' -A "${pkg_arch}" --list-format '${version}' \
	           list "${platform}" "${pkg_name}")
    fi
    echo "rep_vers = ${rep_vers}"

    # Publish
    if [ "${pkg_vers}" != "${rep_vers}" ]
    then
	echo "Version ${pkg_vers} not in repo, adding..."
	
	# Publish deb
	reprepro -s includedeb "${platform}" "${pkg_path}" > /dev/null
	if [ $? -ne 0 ]
	then
	    echo "Publishing deb failed!"
	    failure=1
	else
	    echo "Publishing deb succeeded!"
	fi

	# Publish dsc
	if [[ -n ${pkg_path} ]]
	then
	    reprepro -s includedsc "${platform}" "${src_path}" > /dev/null
	    if [ $? -ne 0 ]
	    then
		echo "Publishing dsc failed!"
		failure=1
	    else
		echo "Publishing dsc succeeded!"
	    fi
	fi
	
    else
	echo "Version ${pkg_vers} already in repo, skipping."
    fi

    # Exit repo directory
    popd

done

# Exit out directory
popd

# Reset GNUPGHOME
if [[ -z "${old_GNUPGHOME}" ]]
then
    unset GNUPGHOME
else
    export GNUPGHOME="${old_GNUPGHOME}"
fi

# Report failure
if [ ${failure} -ne 0 ]
then
    echo "There were build errors..."
fi

exit ${failure}
