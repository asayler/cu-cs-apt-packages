cu-cs-apt-packages
==================

APT Packages for University of Colorado CS Courses

To update changelog
-------------------
* From 'debian' package directory
* Run 'dch -i'

To export repo
--------------
* From pakcage git repo
* Run 'git checkout-index -a -f --prefix=/home/andy/build/'

To build package
----------------
* From 'debian' package directory
* Run 'equivs-build -f control'

To add deb package to repo
--------------------------
* From '/var/www/apt/ubuntu' directory
* Run 'reprepro includedeb precise ~/build/PATH/NAME.deb'

To add source package to repo
-----------------------------
* From '/var/www/apt/ubuntu' directory
* Run 'reprepro includedsc precise ~/build/PATH/NAME.dsc'

To list repo packages
---------------------
* From '/var/www/apt/ubuntu' directory
* Run 'reprepro list precise'
