import click
import subprocess
import http.server
import socketserver
from .build_main import do_build
import os
from .config_reader import load_config
from datetime import datetime
from .jinja_template_inject import jinja_template_inject

config = None

@click.group()
@click.argument('config_path')
def cli(config_path):
    global config
    config = load_config(config_path)
    pass

@cli.command()
def build():
    do_build()

@cli.command()
def build_serve():
    do_build()
    output_folder = config['output_folder']
    subprocess.run('cd {output_folder} && python3 -m http.server'.format(output_folder=output_folder), shell=True, check=True)

@cli.command(help='$name')
@click.argument('name')
def new_post(name):
    # haveing this doc string does the same as the help kwa """laskjdf"""
    click.echo('create new post from template')
    today = datetime.now(tz=None) 
    injects = {'date': today.strftime('%Y-%m-%d')}
    jinja_template_inject('./content/templates/post_template.md',
            './content/posts/{name}.md'.format(name=name),
            injects)
    return
    bashCommand = 'cp ./content/templates/post_template.md ./content/posts/{name}.md'.format(name=name)
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(output, error)

if __name__ == '__main__':
    cli()

def main():
    cli()

