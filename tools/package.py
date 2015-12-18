#!/usr/bin/env python3

import os
import os.path
import subprocess
import shutil
import urllib

import click
import requests

import cu_apt

_ENCODING = "utf-8"

_DEFAULT_BUILD_DIR = "/tmp/pkg-build"
_DEFAULT_SOURCE_DIR = "./"
_DEFAULT_URLS_FILE = "./thirdparty.urls"
_DEFAULT_PREBUILT_DIR = "./prebuilt"
_DEFAULT_REPO_DIR = "/srv/apt/ubuntu"

_DEB_DIR = "debian"
_BUILD_SRC_DIR = "src"
_BUILD_PKG_DIR = "pkg"

_DEB_BUILD_EXTS = ['.deb', '.dsc', '.changes', '.gz', '.tar']

@click.group()
@click.option('--build_dir', default=_DEFAULT_BUILD_DIR, type=str, help="Build Directory")
@click.option('--gpg_dir', default=None, type=str, help="GPG Home Directory")
@click.pass_context
def cli(ctx, build_dir, gpg_dir):
    """
    Top level CLI Wrapper

    """

    ctx.obj = {}
    ctx.obj['build_dir'] = os.path.abspath(build_dir)
    
    if gpg_dir:
        ctx.obj['gpg_dir'] = os.path.abspath(gpg_dir)
        click.secho("Setting GNUPGHOME to '{}'".format(ctx.obj['gpg_dir']))
        os.environ['GNUPGHOME'] = ctx.obj['gpg_dir']


@click.command()
@click.pass_obj
def clean(obj):
    """
    Clean Build Directory

    """

    build_dir = obj['build_dir']
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

@click.command()
@click.option('--source_dir', default=_DEFAULT_SOURCE_DIR, type=str,
              help="Package Source Directory")
@click.option('--force', '-f', is_flag=True, type=bool,
              help="Force Build of All Packages")
@click.argument('package_names', default=None, nargs=-1, type=str)
@click.pass_obj
def build(obj, source_dir, force, package_names):
    """
    Build Packages

    """

    # Setup Paths and Vars
    bld_dir = obj['build_dir']
    src_dir = os.path.abspath(source_dir)
    exp_dir = os.path.join(bld_dir, _BUILD_SRC_DIR)
    out_dir = os.path.join(bld_dir, _BUILD_PKG_DIR)
    os.makedirs(out_dir, exist_ok=True)
    pkgs_succeeded = []
    pkgs_skipped = []
    pkgs_failed = []

    # Export Source via Git
    cmd = ["git", "checkout-index", "-a", "-f", "--prefix={}/".format(exp_dir)]
    proc = subprocess.Popen(cmd, cwd=src_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode:
        raise click.ClickException("Git Export Failed")

    # Find Package Sources
    src_repo = cu_apt.src_repo(exp_dir)

    # Find Built Packages
    deb_repo = cu_apt.deb_repo(out_dir)

    # Filter Packages
    pkgs_queued = []
    if package_names:
        for pkg_name in sorted(package_names):
            if pkg_name in src_repo:
                pkgs_queued.append(pkg_name)
            else:
                click.secho("Could Not Find Package '{}'".format(pkg_name), err=True, fg='red')
                pkgs_failed.append(pkg_name)
    else:
        pkgs_queued += src_repo.keys()

    # Find Newer Sources
    if not force:
        for pkg_name in sorted(pkgs_queued):
            if pkg_name in deb_repo:
                pkg_ver = src_repo[pkg_name].vers
                deb_ver = deb_repo[pkg_name].vers
                if pkg_ver <= deb_ver:
                    click.secho("Skipping {}: Version {} already built".format(pkg_name, deb_ver),
                                fg='yellow')
                    pkgs_skipped.append(pkg_name)
                    pkgs_queued.remove(pkg_name)

    # Build Packages
    cmd = ["equivs-build", "-f", "control"]
    for pkg_name in sorted(pkgs_queued):
        pkg_src_dir = src_repo[pkg_name].path
        deb_src_dir = os.path.join(pkg_src_dir, _DEB_DIR)
        click.secho("Building {}...".format(pkg_name), fg='blue')
        proc = subprocess.Popen(cmd, cwd=deb_src_dir,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode:
            click.secho("{} Build Failed".format(pkg_name), err=True, fg='red')
            click.secho(stderr.decode(_ENCODING), err=True, fg='red')
            pkgs_failed.append(pkg_name)
        else:
            click.secho("{} Build Succeeded".format(pkg_name), fg='green')
            pkgs_succeeded.append(pkg_name)
            for src_name in os.listdir(deb_src_dir):
                src_path = os.path.join(deb_src_dir, src_name)
                if os.path.splitext(src_path)[1] in _DEB_BUILD_EXTS:
                    dst_path = os.path.join(out_dir, src_name)
                    if os.path.exists(dst_path):
                        os.remove(dst_path)
                    shutil.move(src_path, dst_path)

    # Print Success/Failure
    click.secho("")
    if pkgs_succeeded:
        pkgs_succeeded.sort()
        click.secho("Succeeded Packages:\n{}".format(pkgs_succeeded), fg='green')
    if pkgs_skipped:
        pkgs_skipped.sort()
        click.secho("Skipped Packages:\n{}".format(pkgs_skipped), fg='yellow')
    if pkgs_failed:
        pkgs_failed.sort()
        click.secho("Failed Packages:\n{}".format(pkgs_failed), err=True, fg='red')


@click.command()
@click.option('--urls_file', default=_DEFAULT_URLS_FILE, type=str, help="File with Package URLs")
@click.pass_obj
def download(obj, urls_file):
    """
    Download Third Party Packages

    """
    
    build_dir = obj['build_dir']
    deb_out_dir = os.path.join(build_dir, _BUILD_PKG_DIR)
    urls_file = os.path.abspath(urls_file)
    pkgs_succeeded = []
    pkgs_failed = []

    # Download Packages
    os.makedirs(deb_out_dir, exist_ok=True)
    with open(urls_file, 'r') as url_fle:
        for line in url_fle:
            line = line.lstrip().rstrip()
            if line:
                parsed = urllib.parse.urlparse(line)
                pkg_name = os.path.basename(parsed[2])
                pkg_path = os.path.join(deb_out_dir, pkg_name)
                click.secho("Downloading {}...".format(pkg_name), fg='blue')
                url = urllib.parse.urlunparse(parsed)
                req = requests.get(url, stream=True)
                if req.status_code == 200:
                    click.secho("{} Download Succeeded".format(pkg_name), fg='green')
                    with open(pkg_path, 'wb') as deb_fle:
                        req.raw.decode_content = True
                        shutil.copyfileobj(req.raw, deb_fle)
                    pkgs_succeeded.append(pkg_name)
                else:
                    click.secho("{} Download Failed: {} Error".format(pkg_name, req.status_code),
                                err=True, fg='red')
                    pkgs_failed.append(pkg_name)

    # Print Success/Failure
    click.secho("")
    if pkgs_succeeded:
        pkgs_succeeded.sort()
        click.secho("Succeeded Packages:\n{}".format(pkgs_succeeded), fg='green')
    if pkgs_failed:
        pkgs_failed.sort()
        click.secho("Failed Packages:\n{}".format(pkgs_failed), err=True, fg='red')

@click.command()
@click.option('--prebuilt_dir', default=_DEFAULT_PREBUILT_DIR, type=str,
              help="Location of prebuilt packages")
@click.pass_obj
def prebuilt(obj, prebuilt_dir):
    """
    Copy prebuilt packages

    """
    
    build_dir = obj['build_dir']
    deb_out_dir = os.path.join(build_dir, _BUILD_PKG_DIR)
    prebuilt_dir = os.path.abspath(prebuilt_dir)
    pkgs_succeeded = []
    pkgs_failed = []

    # Copy Packages
    os.makedirs(deb_out_dir, exist_ok=True)
    for root, dirs, files in os.walk(prebuilt_dir):
        for fle in files:
            base, ext = os.path.splitext(fle)
            if ext == ".deb":
                src = os.path.join(root, fle)
                shutil.copy(src, deb_out_dir)
                pkgs_succeeded.append(base)
            else:
                click.secho("Skipping: {}".format(fle), fg='yellow')

    # Print Success/Failure
    click.secho("")
    if pkgs_succeeded:
        pkgs_succeeded.sort()
        click.secho("Succeeded Packages:\n{}".format(pkgs_succeeded), fg='green')
    if pkgs_failed:
        pkgs_failed.sort()
        click.secho("Failed Packages:\n{}".format(pkgs_failed), err=True, fg='red')

@click.command()
@click.option('--repo_dir', default=_DEFAULT_REPO_DIR, type=str, help="Path to Repo")
@click.option('--release', prompt=True, type=str, help="Release to Publish")
@click.option('--major_vers', default=None, type=str, help="Versions to Publish")
@click.pass_obj
def publish(obj, repo_dir, release, major_vers):
    """
    Publish Packages to Repo
    
    """

    # Setup Paths and Vars
    bld_dir = obj['build_dir']
    out_dir = os.path.join(bld_dir, _BUILD_PKG_DIR)
    repo_dir = os.path.abspath(repo_dir)
    pkgs_succeeded = []
    pkgs_skipped = []
    pkgs_failed = []

    def get_repo_info(pkg_name, pkg_arch, release, attribute):
        cmd = ["reprepro", "-T", "deb", "-A", "{}".format(pkg_arch),
               "--list-format", "'${{{}}}'".format(attribute),
               "list", "{}".format(release), "{}".format(pkg_name)]
        proc = subprocess.Popen(cmd, cwd=repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if err:
            click.secho(err.decode(_ENCODING), err=True, fg='red')
        if proc.returncode:
            raise click.ClickException("reprepro List Failed")
        return out.decode(_ENCODING).lstrip().rstrip().lstrip("'").rstrip("'")

    def repo_publish_deb(pkg_path, release):
        cmd = ["reprepro", "-s", "includedeb",
               "{}".format(release), "{}".format(pkg_path)]
        proc = subprocess.Popen(cmd, cwd=repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if err:
            click.secho(err.decode(_ENCODING), err=True, fg='red')
        if proc.returncode:
            raise click.ClickException("reprepro Publish Failed")
        return out.decode(_ENCODING).lstrip().rstrip()

    def repo_publish_dsc(pkg_path, release):
        cmd = ["reprepro", "-s", "includedsc",
               "{}".format(release), "{}".format(pkg_path)]
        proc = subprocess.Popen(cmd, cwd=repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode:
            click.secho(err.decode(_ENCODING), err=True, fg='red')
            raise click.ClickException("reprepro Publish Failed")
        return out.decode(_ENCODING).lstrip().rstrip()

    # Setup Source Repos
    deb_repo = cu_apt.deb_repo(out_dir)

    # Publish Packages
    for pkg_name in sorted(deb_repo):

        # Get Package Info
        pkg = deb_repo[pkg_name]
        click.secho("Publishing {}...".format(pkg_name), fg='blue')

        # Filter Packages
        if major_vers:
            pkg_major_vers = pkg.vers.split('.')[0]
            if pkg_major_vers != major_vers:
                click.secho("Skipping: Wrong Major Version {}".format(pkg_major_vers), fg='yellow')
                pkgs_skipped.append(pkg_name)
                continue

        # Get Repo Version
        if pkg.arch == "all":
            repo_vers_amd64 = get_repo_info(pkg_name, "amd64", release, "version")
            repo_vers_i386 = get_repo_info(pkg_name, "i386", release, "version")
            if repo_vers_amd64 != repo_vers_i386:
                click.secho("Architecture Version Mismatch", err=True, fg='red')
                pkgs_failed.append(pkg_name)
                continue
            else:
                repo_vers = repo_vers_amd64
        else:
            repo_vers = get_repo_info(pkg_name, pkg.arch, release, "version")

        # Compare Versions
        if pkg.vers == repo_vers:
            click.secho("Skipping: Version {} already in repo.".format(pkg.vers), fg='yellow')
            pkgs_skipped.append(pkg_name)
            continue

        # Publish
        repo_publish_deb(pkg.path, release)
        click.secho("Publishing {} deb Succeeded".format(pkg_name), fg='green')

        # Publish Source
        # ToDo

        pkgs_succeeded.append(pkg_name)

    # Print Success/Failure
    click.secho("")
    if pkgs_succeeded:
        pkgs_succeeded.sort()
        click.secho("Succeeded Packages:\n{}".format(pkgs_succeeded), fg='green')
    if pkgs_skipped:
        pkgs_skipped.sort()
        click.secho("Skipped Packages:\n{}".format(pkgs_skipped), fg='yellow')
    if pkgs_failed:
        pkgs_failed.sort()
        click.secho("Failed Packages:\n{}".format(pkgs_failed), err=True, fg='red')


# CLI Commands
cli.add_command(clean)
cli.add_command(build)
cli.add_command(download)
cli.add_command(prebuilt)
cli.add_command(publish)


# Main
if __name__ == '__main__':
    cli()
