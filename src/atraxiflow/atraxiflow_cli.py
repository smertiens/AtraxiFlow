#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import os

import click
import logging
import colorama
from atraxiflow import __version__ as ax_version
from atraxiflow.logging import set_level
from atraxiflow.core import Workflow, WorkflowContext
from atraxiflow.creator import creator as ax_creator, wayfiles
from atraxiflow.exceptions import *
from atraxiflow.preferences import PreferencesProvider
from contemply.cli import prompt
from contemply.frontend import TemplateParser


@click.group()
def cli():
    pass


@cli.command('creator')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, help='Increase verbosity')
def creator(verbose):
    if verbose:
        set_level(logging.DEBUG)

    ax_creator.launch_app()


@cli.command('run')
@click.argument('filename', type=click.Path(exists=True))
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, help='Increase verbosity')
def run(filename, verbose):
    if verbose:
        set_level(logging.DEBUG)

    nodes = wayfiles.load(filename)
    wf = Workflow(nodes)
    wf.run()


@cli.command('create')
@click.argument('what', type=click.Choice(['extension', 'node']))
def create(what):
    parser = TemplateParser()

    if what == 'extension':
        tpl = os.path.join(os.path.dirname(__file__), 'templates', 'extension.pytpl')
        parser.parse_file(tpl)
    elif what == 'node':
        tpl = os.path.join(os.path.dirname(__file__), 'templates', 'node.pytpl')
        parser.parse_file(tpl)


@cli.command('add-extension')
@click.argument('package_name')
def add_extension(package_name):
    ctx = WorkflowContext()

    try:
        ctx.get_extension_module(package_name)
    except ExtensionException:
        print(colorama.Fore.RED + 'Error: Could not load extension "{}".'.format(package_name) + colorama.Fore.RESET)
        return

    pref = PreferencesProvider()
    ext = pref.get('extensions', ['atraxiflow.base'])
    ext.append(package_name)
    pref.set('extensions', ext)
    pref.save()

    print(colorama.Fore.GREEN + '√ ' + colorama.Fore.RESET + 'Added new extension %s' % package_name)


@cli.command('list-extensions')
def list_extensions():
    pref = PreferencesProvider()
    ext = pref.get('extensions', ['atraxiflow.base'])

    print('Currently the following extensions are registered and available in Creator: \n')

    for l in ext:
        print('* %s' % l)


@cli.command('reset-settings')
def reset_settings():
    if prompt('Are you sure you want to reset all settings?', 'No') is not True:
        return

    pref = PreferencesProvider()
    f = pref._get_settings_file('settings.json')

    if os.path.exists(f):
        os.unlink(f)
        print(colorama.Fore.GREEN + '√ ' + colorama.Fore.RESET + 'Settings were reset.')
    else:
        print('No settings file found.')


@cli.command('version')
def version():
    print(ax_version)


def header():
    h = '\n'.join([
        '*' * 40,
        '*' + 'AtraxiFlow {0}'.format(ax_version).center(38) + '*',
        '*' * 40,
        ''
    ])

    print(h)


def main():
    colorama.init()
    header()
    cli()


if __name__ == '__main__':
    main()
