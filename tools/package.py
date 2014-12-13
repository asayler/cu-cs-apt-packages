#!/usr/bin/env python3

import os
import os.path
import subprocess
import shutil

import click
import debian.changelog

_ENCODING = "utf-8"

_DEFAULT_BUILD_DIR = "/tmp/cu-cs-pkg-build"
_DEFAULT_SOURCE_DIR = "./"

_DEB_DIR = "debian"
_BUILD_SRC_DIR = "src"
_BUILD_PKG_DIR = "pkg"

@click.group()
@click.option('--gpg_dir', default=None, type=str, help="GPG Home Directory")
@click.pass_context
def cli(ctx, gpg_dir):
    
    if gpg_dir:
        gpg_dir = os.path.abspath(gpg_dir)
        click.secho("Setting GNUPGHOME to '{}'".format(gpg_dir))
        os.environ['GNUPGHOME'] = gpg_dir

@click.command()
@click.option('--source_dir', default=_DEFAULT_SOURCE_DIR, type=str, help="Source Directory")
@click.option('--build_dir', default=_DEFAULT_BUILD_DIR, type=str, help="Build Directory")
@click.pass_obj
def build(obj, source_dir, build_dir):

    source_dir = os.path.abspath(source_dir)
    build_dir = os.path.abspath(build_dir)

    # Clean Prior Run
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    # Export Source
    export_dir = os.path.join(build_dir, _BUILD_SRC_DIR)
    cmd = ["git", "checkout-index", "-a", "-f", "--prefix={}/".format(export_dir)]
    proc = subprocess.Popen(cmd, cwd=source_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode:
        raise click.ClickException("Git Export Failed")

    # Find Packages
    packages = []
    for root, dirs, files in os.walk(export_dir):
        pkg_dir = os.path.join(root, _DEB_DIR)
        if os.path.isdir(pkg_dir):
            packages.append(root)
    print(packages)

    # Build Packages
    succeeded = []
    failed = []
    deb_out_dir = os.path.join(build_dir, _BUILD_PKG_DIR)
    cmd = ["equivs-build", "-f", "control"]
    for pkg_src_dir in packages:
        pkg_name = os.path.basename(pkg_src_dir)
        click.secho("Building {}...".format(pkg_name), fg='blue')
        deb_src_dir = os.path.join(pkg_src_dir, _DEB_DIR)
        proc = subprocess.Popen(cmd, cwd=deb_src_dir,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode:
            click.secho("{} Build Failed".format(pkg_name), err=True, fg='red')
            click.secho(stderr.decode(_ENCODING), err=True, fg='red')
            failed.append(pkg_name)
        else:
            click.secho("{} Build Succeeded".format(pkg_name), fg='green')
            succeeded.append(pkg_name)

    if succeeded:
        click.secho("Succeeded Packages: {}".format(succeeded), fg='green')
    if failed:
        click.secho("Failed Packages: {}".format(failed), err=True, fg='red')
        
    
# CLI Commands
cli.add_command(build)

if __name__ == '__main__':
    cli()
