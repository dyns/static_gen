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

from .file_sys import load_config

from . import partial_renderer

def generate_archive_html(processed_posts, posts_slug, post_previews):
    archive_html = ''
    buf = []

    for post, preview in zip(processed_posts, post_previews):
        url = './' + posts_slug + '/'+ post[2]
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

def generate_topic_to_posts_table(processed_posts):
    topics_to_posts = defaultdict(list)
    for (title,_,post_file_name,topics_of_post) in processed_posts:
        for topic in topics_of_post:
            topics_to_posts[topic].append((title, post_file_name))
    return topics_to_posts

def generate_topic_pages_links(topics_slug, post_topics):
    topic_slugs = [s.lower().replace(' ', '_') for s in post_topics]
    topic_links = ['{topics_slug}/{slug}.html'.format(topics_slug=topics_slug, slug=slug) for (slug, name) in zip(topic_slugs, post_topics)]
    topic_anchor_tags = ['<a href="/{topic_link}">{name}</a>'.format(topic_link=topic_link, name=name) for (topic_link, name) in zip(topic_links, post_topics)]
    return (topic_links, topic_anchor_tags)

def format_topics_html(topic_anchor_tags):
    return ['{l}<br />'.format(l=l) for l in topic_anchor_tags]

def do_build(config):
    
    DATE_FORMAT = str(config['post_date_display_format'])

    # generate paths via join with content root
    posts_folder = str(config['posts_folder'])
    pages_folder = str(config['pages_folder'])
    static_folder = str(config['static_folder'])
    templates_folder = str(config['templates_folder'])
    partials_folder = str(config['partials_folder'])
    output_folder = str(config['output_folder'])
    posts_slug = str(config['posts_slug'])
    archive_out_slug = str(config['archive_out_slug'])
    archive_out_title = str(config['archive_out_title'])
    site_name = str(config['site_name'])
    topics_slug = str(config['topics_slug'])
    config_tabs = config['tabs']


    posts_output_folder = output_folder + '/' + posts_slug
    topics_output_folder = output_folder + '/' + topics_slug

    #load all files in html partials
    head_include_html = load_file_string(os.path.join(partials_folder, 'head_include.html'))
    footer_html = load_file_string(os.path.join(partials_folder, 'footer.html'))
    header_html = load_file_string(os.path.join(partials_folder, 'header.html'))
    topics_template = load_file_string(os.path.join(partials_folder, 'topic_list.html'))

    templates_html = []

    for file in os.listdir(partials_folder):
        html_text_r = load_file_string(os.path.join(partials_folder, file))
        file = file.replace('.', '_')
        templates_html.append((file, html_text_r))


    #load template paths
    post_template_path = os.path.join(templates_folder, 'post_template.html')
    topic_template_path = os.path.join(templates_folder, 'topic_template.html')
    archive_template_path = os.path.join(templates_folder, 'archive_template.html')
    pages_template_path = os.path.join(templates_folder, 'pages_template.html')
    j_pages_template_path = os.path.join(templates_folder, 'pages_template.html')

    # load static files first
    #shutil.copytree(src, dst, symlinks=False, ignore=None, copy_function=copy2, ignore_dangling_symlinks=False)
    shutil.rmtree(output_folder, ignore_errors=True, onerror=None)
    shutil.copytree(static_folder, output_folder, symlinks=False, ignore=None, copy_function=shutil.copy, ignore_dangling_symlinks=False)


    # redner header with jinja with additional tabs in config
    header_html = partial_renderer.gen(header_html, {'tabs': config_tabs, 'site_name':site_name})

    partials = {'head_include':head_include_html, 'footer': footer_html, 'header': header_html, 'topics_template': topics_template}

    # create posts folder
    os.mkdir(posts_output_folder, mode=0o700)
    
    # inflate posts
    (post_topics, processed_posts, post_previews) = process_posts(DATE_FORMAT, posts_folder, posts_output_folder, post_template_path, partials)


    def process_pages(pages_dir, injects):
        for file_name in os.listdir(pages_dir):
            if file_name.endswith('.md'):
                full_path = os.path.join(pages_dir, file_name)
                with open(full_path, 'r') as f:
                    new_name = file_name[:-3].replace(' ', '_') + '.html'
                    # convert md to html
                    html_content = markdown.markdown(f.read())
                    injects.update({'content':html_content, 'title': site_name, 'site_name':site_name})
                    out_path = os.path.join(output_folder, new_name)

                    if 'index' in full_path:
                        jinja_template_inject(j_pages_template_path, out_path, injects)
                        #template = Template(html_content)
                        #s = template.render(**injects)
                        #my_write_string_to_file(out_path, s)
                    else:
                        template_inject(injects, 
                            pages_template_path,
                            out_path)

    # inflate pages
    process_pages(pages_folder, partials)

    # sort posts by date
    zipped = sorted(zip(processed_posts, post_previews), key=lambda x: x[0][1], reverse=True)

    if zipped:
        processed_posts, post_previews = zip(*zipped)
    else:
        processed_posts = []
        post_previews = []

    # generate topic pages links
    (topic_links, topic_anchor_tags) = generate_topic_pages_links(topics_slug, post_topics)

    # generate topic anchor tags for side bar
    topics_to_posts = generate_topic_to_posts_table(processed_posts)

    topics_html = format_topics_html(topic_anchor_tags)
    topics_html = ''.join(topics_html)

    #topic_list_html_jinja = partial_renderer.gen(topics_template, {'topic_data': zip(post_topics, topic_links), 'topic_links': topic_links, 'topic_names': post_topics})

    new_injects = {}
    new_injects.update({'topic_data': zip(post_topics, topic_links), 'topic_links': topic_links, 'topic_names': post_topics})
    new_injects.update({'tabs': config_tabs, 'site_name':site_name})
    asd = [ (partial_name, partial_renderer.gen(partial_html, new_injects)) for (partial_name, partial_html) in templates_html]


    #inject achive_html to archive_template
    archive_html = generate_archive_html(processed_posts, posts_slug, post_previews)
    inject_data = {'site_name':site_name, 'content': archive_html, 'head_include': head_include_html, 'header':header_html, 'footer':footer_html, 'title':archive_out_title}
    inject_data.update(asd)

    # archive template inflate
    #template_inject(inject_data, archive_template_path,
    #     os.path.join(output_folder, archive_out_slug))

    jinja_template_inject(archive_template_path, os.path.join(output_folder, archive_out_slug), inject_data)

    # create topics folder
    os.mkdir(topics_output_folder, mode=0o700)

    # inflate topic pages
    for (topic, topic_link) in zip(post_topics, topic_links):
        topic_content = ['<a href="/{posts_slug}/{post_slug}">{post_name}</a>'.format(posts_slug=posts_slug, post_slug=post_slug,post_name=post_name) for (post_name, post_slug) in topics_to_posts[topic]]
        topic_content = '<br />'.join(topic_content)
        inject_data.update({'content': topic_content, 'title': topic})
        template_inject(inject_data, topic_template_path, os.path.join(output_folder, topic_link))





