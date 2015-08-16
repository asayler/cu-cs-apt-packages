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
* ./tools/requirements.txt

Auto Build
----------

To build and publish automatically, run:

    # Make Tmp Directory
    $ mkdir /tmp/packages

    # Download Third Party Packages
    $ ./tools/package.py --build_dir /tmp/packages --gpg_dir <KEYS> download --urls_file ./repos/<REPO>/thirdparty.urls

    # Build CU CS Packages
    $ ./tools/package.py --build_dir /tmp/packages --gpg_dir <KEYS> build --source-dir ./repos/<REPO>/

    # Publish Packages
    $ ./tools/package.py --build_dir /tmp/packages --gpg_dir <KEYS> publish --repo_dir /srv/apt/ubuntu/ --release <RELEASE>

Old ways; deprecated:

    (precise) ./build && ./publish
    (trusty) ./build_cu-cs.sh && ./get_thirdparty.sh && ./publish_all.sh

Manual Build
------------

To build manually, see steps below.

### To Setup GPG Agent

Install gpg-agent (Debian/Ubuntu):

    sudo apt-get install gnupg-agent

Add the following to ~/.profile (Debian/Ubuntu):

    # GPG Agent
    echo "Setting Up GPG Agent"
    eval $(gpg-agent --enable-ssh-support --daemon)

Add the following to ~/.bashrc:

    # GPG Agent Setup
    GPG_TTY=$(tty)
    export GPG_TTY

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
