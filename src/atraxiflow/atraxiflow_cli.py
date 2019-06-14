#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.creator import creator_main
import click

@click.group()
def cli():
    pass

@cli.command('creator')
def creator():
    creator_main.launch_app()

if __name__ == '__main__':
    cli()
