import click
import subprocess
import http.server
import socketserver
from .build_main import do_build
import os
from datetime import datetime
from .jinja_template_inject import jinja_template_inject
from .file_sys import load_config
from pathlib import Path
from .config_help import write_default_config
import sys

'''
config = None

@cli.group()
@click.option('--config', 'config_path', default='./config.yaml', show_default=True)
def generator(config_path):
    global config
    config = load_config(config_path)
    pass
'''

@click.group()
def cli():
    pass

@cli.command()
@click.option('--path', 'config_path', default='./config.yaml', show_default=True)
def copy_default_config(config_path):
    config_path = os.path.abspath(config_path)
    path = Path(config_path)
    if path.exists():
        print('Path {} already exists.'.format(config_path))
    else:
        write_default_config(config_path)

'''
# generate content folder based off of config
@cli.command()
@click.option('--config', 'config_path', default='./config.yaml', show_default=True)
def generate_content_dir(config_path):
    # get desired content directory from config
    config = load_config(config_path)
    content_path = Path(config['config_folder'])

    # create content root if doesn't exist
    content_path.mkdir(parents=True, exist_ok=True)

    if content_path.is_dir():
        def create_subcontent_dir(root, relative):
            path = Path(os.path.join(root, relative))
            path.mkdir(parents=True, exist_ok=True)
        # create each directory
        create_subcontent_dir(content_path, config['posts_folder'])
        create_subcontent_dir(content_path, config['pages_folder'])
        create_subcontent_dir(content_path, config['static_folder'])
        create_subcontent_dir(content_path, config['templates_folder'])
        create_subcontent_dir(content_path, config['partials_folder'])
    else:
        print("Content folder {} doesn't exist, please create root content directory.".format(content_path))
        sys.exit(1)
'''

@cli.command()
@click.argument('title')
@click.option('--config', 'config_path', default='./config.yaml', show_default=True)
def new_post(title, config_path):
    config = load_config(config_path)
    posts_path = Path(config['posts_folder'])

    # todo: actually format title for file name
    file_name = '{}.md'.format(title.strip().lower())

    new_post_path = os.path.join(posts_path, file_name)

    today = datetime.now(tz=None) 
    injects = {'date': today.strftime('%Y-%m-%d'), 'title': title}

    # get path of static template resource
    post_template_res = os.path.join(os.path.dirname(__file__), './res/post_template.md')

    jinja_template_inject(post_template_res, new_post_path, injects)

    print('Created {} in {}'.format(file_name, posts_path))


@cli.command()
@click.option('--config', 'config_path', default='./config.yaml', show_default=True)
def build(config_path):
    config = load_config(config_path)
    do_build(config)

@cli.command()
@click.option('--config', 'config_path', default='./config.yaml', show_default=True)
def build_serve(config_path):
    config = load_config(config_path)
    do_build(config)
    output_folder = config['output_folder']
    subprocess.run('cd {output_folder} && python3 -m http.server'.format(output_folder=output_folder), shell=True, check=True)

if __name__ == '__main__':
    cli()

def main():
    cli()


