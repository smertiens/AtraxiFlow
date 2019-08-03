#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import click
import os
from atraxiflow.creator import creator as ax_creator, wayfiles
from contemply.frontend import TemplateParser

@click.group()
def cli():
    pass


@cli.command('creator')
def creator():
    ax_creator.launch_app()


@cli.command('run')
@click.argument('filename')
def run(filename):
    wf = wayfiles.load_as_workflow(filename)
    wf.run()

@cli.command('create')
@click.argument('what')
def create(what):
    if create == 'package':
        tpl = os.path.join(os.path.dirname(__file__), 'templates', 'package.pytpl')
        parser = TemplateParser()
        parser.parse_file(tpl)
    else:
        # show help
        pass


def main():
    cli()


if __name__ == '__main__':
    main()
