cu-cs-apt-packages
==================

APT Packages for University of Colorado CS Courses

To build automatically, export the repo and then run:

'./build; ./install' from the build directory.

To build manually, see steps below.

To update changelog
-------------------
* From 'debian' package directory
* Run 'dch -i'

To export repo
--------------
* From 'packages' git repo
* Run 'git checkout-index -a -f --prefix=PATH/build/'

To build package
----------------
* From 'debian' package directory
* Run 'equivs-build -f control'

To add deb package to repo
--------------------------
* From '/var/www/apt/ubuntu' directory
* Run 'reprepro includedeb precise PATH/build/PATH/NAME.deb'

To add source package to repo
-----------------------------
* From '/var/www/apt/ubuntu' directory
* Run 'reprepro includedsc precise PATH/build/PATH/NAME.dsc'

To list repo packages
---------------------
* From '/var/www/apt/ubuntu' directory
* Run 'reprepro list precise'
