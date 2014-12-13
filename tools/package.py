#!/usr/bin/env python3

import os
import os.path
import subprocess
import shutil

import click
import debian.changelog

_DEFAULT_BUILD_DIR = "/tmp/cu-cs-pkg-build"
_DEFAULT_SOURCE_DIR = "./"

_PACKAGE_DIR = "debian"
_BUILD_SRC_DIR = "src"
_BUILD_PGK_DIR = "pkg"

@click.group()
@click.pass_context
def cli(ctx):
    pass

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
        pkg_dir = os.path.join(root, _PACKAGE_DIR)
        if os.path.isdir(pkg_dir):
            packages.append(root)
    print(packages)
    
    
# CLI Commands
cli.add_command(build)

if __name__ == '__main__':
    cli()
