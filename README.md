cu-cs-apt-packages
==================

APT Packages for University of Colorado CS Courses

Published at http://apt.cs.colorado.edu

Andy Sayler (http://www.andysayler.com) <br />
Matt Monaco (http://ngn.cs.colorado.edu/~matt/)

Requirements
------------

* reprepro
* equivs

Auto Build
----------

To build and publish automatically, run:

    (precise) ./build && ./publish
    (trusty) ./build_cu-cs.sh && ./get_thirdparty.sh && ./publish_all.sh

Manual Build
------------
To build manually, see steps below.

### To Update changelog

From 'debian' package directory, run:

    dch -i

### To export repo

From 'packages' git repo, run:

    git checkout-index -a -f --prefix=PATH/build/

### To build package

From 'debian' package directory, run:

    equivs-build -f control

### To add deb package to repo

From '/var/www/apt/ubuntu' directory, run:

    reprepro includedeb precise PATH/build/PATH/NAME.deb

### To add source package to repo

From '/var/www/apt/ubuntu' directory, run:

    reprepro includedsc precise PATH/build/PATH/NAME.dsc

### To list repo packages

From '/var/www/apt/ubuntu' directory, run:

    reprepro list precise
