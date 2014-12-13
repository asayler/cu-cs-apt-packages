#!/usr/bin/env python3

import os
import os.path
import subprocess
import shutil
import urllib

import click
import requests
import debian.changelog

_ENCODING = "utf-8"

_DEFAULT_BUILD_DIR = "/tmp/pkg-build"
_DEFAULT_SOURCE_DIR = "./"
_DEFAULT_URLS_FILE = "./thirdparty.urls"
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

    ctx.obj = {}
    ctx.obj['build_dir'] = os.path.abspath(build_dir)
    
    if gpg_dir:
        ctx.obj['gpg_dir'] = os.path.abspath(gpg_dir)
        click.secho("Setting GNUPGHOME to '{}'".format(ctx.obj['gpg_dir']))
        os.environ['GNUPGHOME'] = ctx.obj['gpg_dir']

@click.command()
@click.pass_obj
def clean(obj):

    build_dir = obj['build_dir']
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)


@click.command()
@click.option('--source_dir', default=_DEFAULT_SOURCE_DIR, type=str, help="Source Directory")
@click.option('--package_name', default=None, type=str, help="Package to build (Defaults to All)")
@click.pass_obj
def build(obj, source_dir, package_name):

    build_dir = obj['build_dir']
    source_dir = os.path.abspath(source_dir)

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

    # Build Packages
    succeeded = []
    failed = []
    deb_out_dir = os.path.join(build_dir, _BUILD_PKG_DIR)
    os.makedirs(deb_out_dir, exist_ok=True)
    cmd = ["equivs-build", "-f", "control"]
    for pkg_src_dir in packages:
        pkg_name = os.path.basename(pkg_src_dir)
        if package_name:
            if not pkg_name == package_name:
                continue
        click.secho("Building {}...".format(pkg_name), fg='blue')
        deb_src_dir = os.path.join(pkg_src_dir, _DEB_DIR)
        proc = subprocess.Popen(cmd, cwd=deb_src_dir,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode:
            click.secho("{} Build Failed".format(pkg_name), err=True, fg='red')
            failed.append(pkg_name)
            click.secho(stderr.decode(_ENCODING), err=True, fg='red')
        else:
            click.secho("{} Build Succeeded".format(pkg_name), fg='green')
            succeeded.append(pkg_name)
            for src_name in os.listdir(deb_src_dir):
                src_path = os.path.join(deb_src_dir, src_name)
                if os.path.splitext(src_path)[1] in _DEB_BUILD_EXTS:
                    dst_path = os.path.join(deb_out_dir, src_name)
                    if os.path.exists(dst_path):
                        os.remove(dst_path)
                    shutil.move(src_path, dst_path)

    # Print Success/Failure
    click.secho("")
    if succeeded:
        click.secho("Succeeded Packages:\n{}".format(succeeded), fg='green')
    if failed:
        click.secho("Failed Packages:\n{}".format(failed), err=True, fg='red')

@click.command()
@click.option('--urls_file', default=_DEFAULT_URLS_FILE, type=str, help="File with Package URLs")
@click.pass_obj
def download(obj, urls_file):
    
    build_dir = obj['build_dir']
    deb_out_dir = os.path.join(build_dir, _BUILD_PKG_DIR)
    urls_file = os.path.abspath(urls_file)

    # Download Packages
    succeeded = []
    failed = []
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
                    succeeded.append(pkg_name)
                    with open(pkg_path, 'wb') as deb_fle:
                        req.raw.decode_content = True
                        shutil.copyfileobj(req.raw, deb_fle)
                else:
                    click.secho("{} Download Failed: {} Error".format(pkg_name, req.status_code),
                                err=True, fg='red')
                    failed.append(pkg_name)

    # Print Success/Failure
    click.secho("")
    if succeeded:
        click.secho("Succeeded Packages:\n{}".format(succeeded), fg='green')
    if failed:
        click.secho("Failed Packages:\n{}".format(failed), err=True, fg='red')

@click.command()
@click.option('--repo_dir', default=_DEFAULT_REPO_DIR, type=str, help="Path to Repo")
@click.option('--release', default=None, type=str, help="Release to Publish")
@click.pass_obj
def publish(obj, repo_dir, release):

    build_dir = obj['build_dir']
    deb_out_dir = os.path.join(build_dir, _BUILD_PKG_DIR)
    repo_dir = os.path.abspath(repo_dir)
    

# CLI Commands
cli.add_command(clean)
cli.add_command(build)
cli.add_command(download)

if __name__ == '__main__':
    cli()
