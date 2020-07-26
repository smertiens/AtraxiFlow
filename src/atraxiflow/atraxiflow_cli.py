#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

# DEBUG
import sys
sys.path.insert(0, '/Users/mephisto/python_projects/atraxi-flow/src')

#import logging
import os

import click
import colorama
from contemply.cli import prompt, user_input
from contemply.frontend import TemplateParser

from atraxiflow import __version__ as ax_version
from atraxiflow.core import WorkflowContext, Workflow
from atraxiflow.wayfiles import Wayfile, WayDefaultWorkflow
from atraxiflow.exceptions import *
from atraxiflow.axlogging import set_level
from atraxiflow.preferences import PreferencesProvider
from atraxiflow.creator_server import server


@click.group()
def cli():
    pass


@cli.command('creator')
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, help='Increase verbosity')
def creator(verbose):
    if verbose:
        set_level(logging.DEBUG)

    srv = server.CreatorServer()
    srv.start()


@cli.command('run')
@click.argument('filename', type=click.Path(exists=True))
@click.option('--verbose', '-v', type=click.BOOL, is_flag=True, help='Increase verbosity')
def run(filename, verbose):
    if verbose:
        set_level(logging.DEBUG)

    wf = Wayfile()
    wf.load(filename)

    # Get a list of available workflows (excluding default workflow)
    if len(wf.workflows) < 1:
        logging.getLogger('core').error('No workflow found. The source file could be corrupted.')
    elif len(wf.workflows) == 1:
        print('No workflows found for running.')
        return

    choose = []
    for workflow in wf.workflows:
        if isinstance(workflow, WayDefaultWorkflow):
            continue

        choose.append(workflow)

    print('The following workflows were found in "%s":\n' % os.path.basename(filename))
    for n, workflow in enumerate(choose):
        print(colorama.Fore.LIGHTYELLOW_EX + '[%s]' % (n + 1) + colorama.Fore.RESET + ' %s' % workflow.get_name())

    while True:
        user_choice = user_input('\nRun workflow: ')

        if user_choice == '':
            print('Quittting.')
            return
        elif user_choice.isnumeric():
            user_choice = int(user_choice)

            if user_choice > 0 and user_choice <= len(choose):
                nodes = [wf_node.node for wf_node in choose[user_choice - 1].nodes]

                print('')
                print('*' * 5 + ' ' + choose[user_choice - 1].get_name() + ' ' + '*' * 5)
                run_workflow = Workflow(nodes)
                run_workflow.run()

                return

        print('Please enter a number between %s and %s' % (1, len(choose)))


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
    f = pref.get_settings_file('settings.json')

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
