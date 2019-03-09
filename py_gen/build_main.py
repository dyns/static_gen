from datetime import datetime
from yaml import load, dump
from yaml import Loader, Dumper
import os
import shutil
import re
from .template_injection import template_inject
from .markdown_parser import split_md_text
from .posts_processor import process_posts, get_post_topics
import markdown
from jinja2 import Template
from collections import defaultdict
from distutils.dir_util import copy_tree
from .topic_formater import generate_topic_pages_links

from .file_sys import load_config

from . import partial_renderer

def generate_archive_html(processed_posts, posts_slug, post_previews):
    archive_html = ''
    buf = []

    for post, preview in zip(processed_posts, post_previews):
        url = '/' + posts_slug + '/'+ post[2]
        p_html = '<div class="archiveEntry"><h3><a href="{}">{}</a></h3> {} <hr /> </div>'.format( url, post[0], preview) #str(post[1]) 
        buf.append(p_html)

    archive_html = '\n'.join(buf)
    return archive_html

def my_write_string_to_file(file_name, s):
    with open(file_name, 'w') as file_out:
        file_out.write(s)

def jinja_template_inject(template_path, out_file_name, injects):
    template_file = open(template_path)
    template_html = template_file.read()
    template_file.close()
    
    template = Template(template_html)

    rendered = template.render(**injects)

    my_write_string_to_file(out_file_name, rendered)

def load_file_string(name):
    contents = ''
    with open(name, 'r') as f:
        contents = f.read()
    return contents

def generate_topic_to_posts_table(processed_posts, post_previews):
    topics_to_posts = defaultdict(list)
    for ((title,_,post_file_name,topics_of_post), post_preview) in zip(processed_posts, post_previews):
        for topic in topics_of_post:
            topics_to_posts[topic].append((title, post_file_name, post_preview))
    return topics_to_posts

def generate_topic_pages_links_old(topics_slug, post_topics):
    topic_slugs = [s.lower().replace(' ', '_') for s in post_topics]
    topic_links = ['{topics_slug}/{slug}'.format(topics_slug=topics_slug, slug=slug) for (slug, name) in zip(topic_slugs, post_topics)]
    topic_anchor_tags = ['<a href="/{topic_link}">{name}</a>'.format(topic_link=topic_link, name=name) for (topic_link, name) in zip(topic_links, post_topics)]
    return (topic_links, topic_anchor_tags)

def format_topics_html(topic_anchor_tags):
    return ['{l}<br />'.format(l=l) for l in topic_anchor_tags]

# returns [('template_name_html', 'the inflated html')]
def inflate_partials(partials_folder, post_topics, topic_links, config_tabs, site_name, google_analytics_id):
    templates_html = {}

    partial_injects = {}
    partial_injects.update({'topic_data': zip(post_topics, topic_links), 'topic_links': topic_links, 'topic_names': post_topics, 'google_analytics_id': google_analytics_id})
    partial_injects.update({'tabs': config_tabs, 'site_name':site_name})

    for file_name in os.listdir(partials_folder):
        html_text_r = load_file_string(os.path.join(partials_folder, file_name))
        file_name = file_name.replace('.', '_')
        templates_html.update({file_name: partial_renderer.gen(html_text_r, partial_injects)})

    return templates_html

# returns path to where new file should be
def create_page_as_folder(output_folder, page_title):
    new_folder_path = os.path.join(output_folder, page_title)
    new_file_path = os.path.join(new_folder_path, 'index.html')
    os.mkdir(new_folder_path, mode=0o700)
    return new_file_path


def clean_output_folder(output_path, build_retain_paths):
    '''
    Create the output folder if needed.
    Remove all files and folders in output folder except for paths named in build_retain_paths in config
    Currently only checks for ignores at top level
    '''
    output_path_abs = os.path.abspath(output_path)

    # create output folder if needed
    if os.path.isdir(output_path_abs) is False:
        os.mkdir(output_path_abs, mode=0o700)

    for file_name in os.listdir(output_path_abs):
        abs_path = os.path.join(output_path_abs, file_name)
        if os.path.isdir(abs_path):
            #print('to delete dir: ', abs_path)
            shutil.rmtree(abs_path, ignore_errors=True, onerror=None)
        else:
            if file_name not in build_retain_paths:
                #print('to delete file: ', abs_path)
                os.remove(abs_path)
            else:
                pass
                #print('ignore delete: ', abs_path)
    

def do_build(config):
    
    DATE_FORMAT = str(config['post_date_display_format'])

    # format theme paths
    theme_root = str(config['theme_root'])

    templates_folder = os.path.join(theme_root, 'templates') #str(config['templates_folder'])
    partials_folder = os.path.join(theme_root, 'partials') #str(config['partials_folder'])
    theme_static_folder = os.path.join(theme_root, 'static') #config['theme_static_folder']

    # generate paths via join with content root
    posts_folder = str(config['posts_folder'])
    pages_folder = str(config['pages_folder'])
    static_folder = str(config['static_folder'])

    output_folder = str(config['output_folder'])
    posts_slug = str(config['posts_slug'])
    archive_out_slug = str(config['archive_out_slug'])
    archive_out_title = str(config['archive_out_title'])
    site_name = str(config['site_name'])
    topics_slug = str(config['topics_slug'])
    config_tabs = config['tabs']

    disqus_embed = config['disqus_embed']

    google_analytics_id = config['google_analytics_id']
   
    posts_output_folder = output_folder + '/' + posts_slug
    topics_output_folder = output_folder + '/' + topics_slug

    #load template paths
    post_template_path = os.path.join(templates_folder, 'post_template.html')
    topic_template_path = os.path.join(templates_folder, 'topic_template.html')
    archive_template_path = os.path.join(templates_folder, 'archive_template.html')
    pages_template_path = os.path.join(templates_folder, 'pages_template.html')
    j_pages_template_path = os.path.join(templates_folder, 'pages_template.html')

    build_retain_paths = config['build_retain_paths']
    #print(build_retain_paths)

    # load static theme files first
    #shutil.copytree(src, dst, symlinks=False, ignore=None, copy_function=copy2, ignore_dangling_symlinks=False)
    clean_output_folder(output_folder, build_retain_paths)

    #shutil.copytree(theme_static_folder, output_folder, symlinks=False, ignore=None, copy_function=shutil.copy, ignore_dangling_symlinks=False)
    copy_tree(theme_static_folder, output_folder)
    # copy user static files
    copy_tree(static_folder, output_folder)

    # create posts folder
    os.mkdir(posts_output_folder, mode=0o700)
    
    post_topics = get_post_topics(posts_folder)
    post_topics = sorted(post_topics)

    # generate topic pages links
    (topic_links, topic_anchor_tags) = generate_topic_pages_links(topics_slug, post_topics)
    
    partials = inflate_partials(partials_folder, post_topics, topic_links, config_tabs, site_name, google_analytics_id)

    # inflate posts
    (post_topics, processed_posts, post_previews) = process_posts(DATE_FORMAT, posts_folder, posts_output_folder, post_template_path, partials, topics_slug, disqus_embed)

    def process_pages(pages_dir, injects):
        for file_name in os.listdir(pages_dir):
            if file_name.endswith('.md'):
                full_path = os.path.join(pages_dir, file_name)
                with open(full_path, 'r') as f:
                    new_title = file_name[:-3].replace(' ', '_')

                    # convert md to html
                    html_content = markdown.markdown(f.read())
                    injects.update({'content':html_content, 'title': site_name, 'site_name':site_name})
                    
                    if 'index' in full_path:
                        # dont create a folder
                        new_file_name = new_title + '.html'
                        out_path = os.path.join(output_folder, new_file_name)
                    else:
                        out_path = create_page_as_folder(output_folder, new_title)
                        # turn page into index page of folder with name
                        #new_folder_path = os.path.join(output_folder, new_title)
                        #out_path = os.path.join(output_folder, new_title, 'index.html')
                        # create folder with name
                        #os.mkdir(new_folder_path, mode=0o700)

                    jinja_template_inject(j_pages_template_path, out_path, injects)

    # inflate pages
    process_pages(pages_folder, partials)

    # sort posts by date
    zipped = sorted(zip(processed_posts, post_previews), key=lambda x: x[0][1], reverse=True)

    if zipped:
        processed_posts, post_previews = zip(*zipped)
    else:
        processed_posts = []
        post_previews = []

    # generate topic anchor tags for side bar
    topics_to_posts = generate_topic_to_posts_table(processed_posts, post_previews)

    #inject achive_html to archive_template
    archive_html = generate_archive_html(processed_posts, posts_slug, post_previews)
    inject_data = {'site_name':site_name, 'archive_content': archive_html, 'archive_out_title':archive_out_title}
    inject_data.update(partials)

    archive_path = create_page_as_folder(output_folder, archive_out_slug)
    jinja_template_inject(archive_template_path, archive_path, inject_data)

    # create topics folder
    os.mkdir(topics_output_folder, mode=0o700)

    # inflate topic pages
    for (topic, topic_link) in zip(post_topics, topic_links):
        #p_html = '<div class="archiveEntry"><h3><a href="/{posts_slug}/{post_slug}">{post_name}</a></h3> {} <hr /> </div>'.format( url, post[0], preview) #str(post[1]) 
        #topic_content = ['<a href="/{posts_slug}/{post_slug}">{post_name}</a>'.format(posts_slug=posts_slug, post_slug=post_slug,post_name=post_name) for (post_name, post_slug, post_preview) in topics_to_posts[topic]]
        topic_content = ['<div class="archiveEntry"><h3><a href="/{posts_slug}/{post_slug}">{post_name}</a></h3> {preview} <hr /> </div>'.format(posts_slug=posts_slug, post_slug=post_slug,post_name=post_name, preview=post_preview) for (post_name, post_slug, post_preview) in topics_to_posts[topic]]
        topic_content = '\n'.join(topic_content)
        inject_data.update({'content': topic_content, 'title': topic})
        topic_page_path = create_page_as_folder(output_folder, topic_link)
        template_inject(inject_data, topic_template_path, topic_page_path)

        #template_inject(inject_data, topic_template_path, os.path.join(output_folder, topic_link))
