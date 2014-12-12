#!/usr/bin/env python3

import click
import debian.changelog

_DEFAULT_BUILD_DIR = "/tmp/cu-cs-pkg-build"

@click.group()
@click.pass_context
def cli(ctx):
    pass

@click.command()
@click.option('--package', default=None, type=str, help="Package to build (Defaults to All)")
@click.option('--build_dir', default=_DEFAULT_BUILD_DIR, type=str, help="Build Directory")
@click.pass_obj
def build(obj, package, build_dir):
    pass

# CLI Commands
cli.add_command(build)

if __name__ == '__main__':
    cli()
