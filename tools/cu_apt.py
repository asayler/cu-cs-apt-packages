import abc
import os
import subprocess

import debian.changelog

_DEB_DIR = "debian"
_CHANGELOG = "changelog"
_ENCODING = "utf-8"


### Helper Functions ###

def _dpkg_field(pkg_path, field):
    cmd = ["dpkg", "-f", "{}".format(pkg_path), "{}".format(field)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode:
        raise click.ClickException("Dpkg Failed")
    return out.decode(_ENCODING).lstrip().rstrip()


### Classes ###

class abc_pkg(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self, path):

        self.path = os.path.abspath(path)
        self.name = None
        self.vers = None

class src_pkg(abc_pkg):

    def __init__(self, path):

        super().__init__(path)
        self.name = os.path.basename(path)
        self.vers = self._find_vers()

    def _find_vers(self):

        change_path = os.path.join(self.path, _DEB_DIR, _CHANGELOG)
        with open(change_path, 'r') as f:
            change_obj = debian.changelog.Changelog(file=f)
        return str(change_obj.version)

class deb_pkg(abc_pkg):

    def __init__(self, path):

        super().__init__(path)
        self.name = _dpkg_field(path, 'Package')
        self.vers = _dpkg_field(path, 'Version')

class abc_repo(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self, path):

        self.path = os.path.abspath(path)
        self.pkgs = None

    def __iter__(self):

        return self.pkgs

    def __contains__(self, key):

        return key in self.pkgs

    def __getitem__(self, key):

        return self.pkgs[key]

    def keys(self):
        
        return self.pkgs.keys()

class src_repo(abc_repo):

    def __init__(self, path):

        super().__init__(path)
        self.pkgs = self._find_pkgs()
        
    def _find_pkgs(self):

        pkgs = {}

        for root, dirs, files in os.walk(self.path):

            deb_dir = os.path.join(root, _DEB_DIR)
            if os.path.isdir(deb_dir):
                pkg = src_pkg(root)
                pkgs[pkg.name] = pkg
            else:
                pass

        return pkgs

class deb_repo(abc_repo):

    def __init__(self, path):

        super().__init__(path)
        self.pkgs = self._find_pkgs()
        
    def _find_pkgs(self):

        pkgs = {}

        for root, dirs, files in os.walk(self.path):

            for fle in files:
                path = os.path.join(root, fle)
                base, ext = os.path.splitext(path)
                if ext == ".deb":
                    pkg = deb_pkg(path)
                    pkgs[pkg.name] = pkg
                else:
                    pass

        return pkgs
