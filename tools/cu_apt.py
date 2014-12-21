import os

import debian.changelog

_DEB_DIR = "debian"
_CHANGELOG = "changelog"


class src_pkg():

    def __init__(self, path):

        self.path = os.path.abspath(path)
        self.name = os.path.basename(path)
        self.vers = self._find_vers()

    def _find_vers(self):

        change_path = os.path.join(self.path, _DEB_DIR, _CHANGELOG)
        with open(change_path, 'r') as f:
            change_obj = debian.changelog.Changelog(file=f)
        return str(change_obj.version)

class src_repo():

    def __init__(self, path):

        self.path = os.path.abspath(path)
        self.pkgs = self._find_pkgs()
        
    def _find_pkgs(self):

        pkgs = []

        for root, dirs, files in os.walk(self.path):

            deb_dir = os.path.join(root, _DEB_DIR)
            if os.path.isdir(deb_dir):
                pkgs.append(src_pkg(root))
            else:
                pass

        return pkgs
