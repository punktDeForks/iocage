# Copyright (c) 2014-2019, iocage
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted providing that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""fetch module for the cli."""
import click
import iocage_lib.ioc_common as ioc_common
import iocage_lib.iocage as ioc
import os

__rootcmd__ = True


def validate_count(ctx, param, value):
    """Takes a string, removes the commas and returns an int."""

    if isinstance(value, str):
        try:
            value = value.replace(",", "")

            return int(value)
        except ValueError:
            ioc_common.logit(
                {
                    "level": "EXCEPTION",
                    "message": f"({value} is not a valid integer."
                })
    else:
        return int(value)


@click.command(
    context_settings=dict(max_content_width=400),
    name="fetch", help="Fetch a version of FreeBSD for jail usage or a"
    " preconfigured plugin."
)
@click.option(
    "--http", "-h", default=True, is_flag=True,
    help="No-op flag for backwards compat"
)
@click.option(
    "--file", "-f", "_file", default=False, is_flag=True,
    help="Use a local file directory for root-dir instead of HTTP"
)
@click.option(
    "--files", "-F", multiple=True,
    help="Specify the files to fetch from the mirror."
)
@click.option(
    "--server", "-s", default="download.freebsd.org",
    help="Server to fetch from."
)
@click.option(
    "--keep_jail_on_failure", "-k", default=False, is_flag=True,
    help="Keep jails on failure"
)
@click.option(
    "--user", "-u", default="anonymous", help="The user to use."
)
@click.option(
    "--password", "-p", default="anonymous@", help="The password to use."
)
@click.option(
    "--auth", "-a", default=None,
    help="Authentication method for HTTP fetching. Valid values:"
         " basic, digest"
)
@click.option(
    "--verify/--noverify", "-V/-NV", default=True,
    help="Enable or disable verifying SSL cert for HTTP fetching."
)
@click.option(
    "--release", "-r", help="The FreeBSD release to fetch."
)
@click.option(
    '--plugin-name', '-P', default=None,
    help='Supply a plugin name for --plugins to fetch or use a'
         ' auto completed filename for --plugin-name.\nAlso accepts full'
         ' path for a plugin file.'
)
@click.option(
    "--plugins", help="List all available plugins for creation.", is_flag=True
)
@click.argument(
    "props", nargs=-1
)
@click.option(
    "--count", "-c", callback=validate_count, default="1",
    help="Designate a number of plugin type jails to create."
)
@click.option(
    "--root-dir", "-d",
    help="Root directory " + "containing all the RELEASEs."
)
@click.option(
    "--update/--noupdate", "-U/-NU", default=True,
    help="Decide whether or not to update the fetch to the latest "
         "patch level."
)
@click.option(
    "--eol/--noeol", "-E/-NE", default=True,
    help="Enable or disable EOL checking with upstream."
)
@click.option(
    '--name', '-n',
    help='Specify which jail name to use. Leave empty for default '
         'selection based on --plugin-name.'
)
@click.option(
    "--accept/--noaccept", default=False,
    help="Accept the plugin's LICENSE agreement."
)
@click.option(
    "--official", "-O", is_flag=True, default=False,
    help="Lists only official plugins."
)
@click.option(
    "--branch", default=None,
    help="Select a different plugin branch (for development)"
)
@click.option(
    "--thickconfig", "-C", default=False, is_flag=True,
    help="Do not use inheritable configuration with plugins"
)
@click.option(
    '--proxy', '-S', default=None,
    help='Provide proxy to use for creating jail'
)
def cli(**kwargs):
    """CLI command that calls fetch_release()"""
    release = kwargs.get("release", None)
    _file = kwargs.get("_file", False)

    proxy = kwargs.pop('proxy')
    if proxy:
        os.environ.update({
            'http_proxy': proxy,
            'https_proxy': proxy
        })

    if release is not None:
        if release.lower() == "latest":
            release = ioc_common.parse_latest_release()
            kwargs["release"] = release

        try:
            float(release.rsplit("-", 1)[0].rsplit("-", 1)[0])
        except ValueError:
            ioc_common.logit({
                "level": "EXCEPTION",
                "message": "Please supply a valid entry."
            })

        if not _file:
            ioc_common.check_release_newer(release)

    ioc.IOCage().fetch(**kwargs)
