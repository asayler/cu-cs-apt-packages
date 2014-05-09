#!/usr/bin/env bash

links="./thirdparty.urls"
failure=0

build_dir="/tmp/thirdparty"
platform="trusty"
working_dir="${build_dir}/${platform}/"

repo_dir="/srv/apt/ubuntu/"

gpgkeys="${HOME}/cu/packages/cu-cs-apt-keys"

# Set GNUPGHOME
old_GNUPGHOME="${GNUPGHOME}"
export GNUPGHOME="${gpgkeys}"

# Cleanup Previous Run
rm -rf "${working_dir}"

# Fetch Package Links
wget -P "${working_dir}" -i "${links}"

pushd "${working_dir}"

for deb in *.deb
do

    echo "Publishing ${deb}..."

    pkg_path=$(readlink -f "${deb}")
    pkg_name=$(dpkg -f "${deb}" 'Package')
    pkg_vers=$(dpkg -f "${deb}" 'Version')
    pkg_arch=$(dpkg -f "${deb}" 'Architecture')

    echo "pkg_path = ${pkg_path}"
    echo "pkg_name = ${pkg_name}"
    echo "pkg_vers = ${pkg_vers}"
    echo "pkg_arch = ${pkg_arch}"    

    pushd "${repo_dir}"

    rep_vers=$(reprepro -T 'deb' -A "${pkg_arch}" --list-format '${version}' \
	       list "${platform}" "${pkg_name}")

    if [ "${pkg_vers}" != "${rep_vers}" ]
    then
	echo "Version ${pkg_vers} not in repo, adding..."
	reprepro -s includedeb "${platform}" "${pkg_path}" > /dev/null
	if [ $? -ne 0 ]
	then
	    echo "Publishing failed!"
	    failure=1
	else
	    echo "Publishing succeeded!"
	fi
    else
	echo "Version ${pkg_vers} already in repo, skipping."
    fi

    popd

done

popd

# Reset GNUPGHOME
if [[ -z "${old_GNUPGHOME}" ]]
then
    unset GNUPGHOME
else
    export GNUPGHOME="${old_GNUPGHOME}"
fi
