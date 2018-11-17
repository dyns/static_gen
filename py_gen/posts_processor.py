'''
Inflates markdown posts, expands syntax for youtube and vimeo injects to html template,
'''

from .jinja_template_inject import jinja_template_inject
import os
from .markdown_parser import split_md_text
from yaml import load
import markdown
from .template_injection import template_inject
import re

def gen_youtube_embed(vid_id):
    text = '<iframe width="640" height="480" src="https://www.youtube-nocookie.com/embed/{}?rel=0" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>'
    return text.format(vid_id)

def gen_vimeo_embed(vid_id):
    text = '<iframe src="https://player.vimeo.com/video/{}?color=1fc9a2&portrait=0" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>'
    return text.format(vid_id)

def youtube_pass(html):
    #{{&lt; youtube qbzSxZ5HkjM &gt;}}
    inject_reg = re.compile('({{&lt;[ ]*(youtube|vimeo)[ ]+([0-9A-Za-z_-]+)[ ]*&gt;}})')
    matches = re.findall(inject_reg, html)
    if matches:
        #print(matches)
        for match in matches:
            total = match[0]
            service = match[1]
            vid_id = match[2]
            replacement = None
            if service == 'youtube':
                replacement = gen_youtube_embed(vid_id)
            elif service == 'vimeo':
                replacement = gen_vimeo_embed(vid_id)
            if replacement:
                html = html.replace(total, replacement)
    return html 



def process_posts(date_format, posts_folder, posts_output_folder, archive_template_path, partials):
    processed_posts = []
    all_topics = set()
    post_header_date_format = '%Y-%m-%d'
    # inflate markdown posts to html
    for file in os.listdir(posts_folder):
        if file.endswith('.md'):
            full_path = os.path.join(posts_folder, file)

            md_file = open(full_path, 'r')

            # todo - inject header info in post html - date and title
            (md_header_text, md_text) = split_md_text(md_file)
            md_file.close()

            title = None
            date = None
            date_text = None

            md_header = load(md_header_text)

            topics = []

            post_to_topics = {}

            if md_header:
                #print(md_header)
                title = md_header['title']
                if 'date' in md_header:
                    date_text = md_header['date']
                if 'topics' in md_header:
                    topics = md_header['topics']
                    topics = [s.title() for s in topics]

            if date_text:
                try:
                    date = date_text#datetime.strptime(date_text, post_header_date_format).date()
                except ValueError:
                    pass

            if title and date and topics is not None:
               
                all_topics.update(topics)

                post_file_name = title.lower().replace(' ', '_') +'.html'
                html_file_name = os.path.join(posts_output_folder, post_file_name)
                post_html = markdown.markdown(text=md_text)

                post_html = youtube_pass(post_html) 

                print_date = date.strftime(date_format)

                partials.update({'title': title, 'print_date':print_date, 'content': post_html})
                '''
                template_inject(partials,
                        archive_template_path,
                        html_file_name)
                '''

                jinja_template_inject(archive_template_path, html_file_name, partials)

                # add to list
                #print('second', list(topics))
                post_data = (title, date, post_file_name, topics)
                processed_posts.append(post_data)

            else:
                error_text = 'post ignored: {} title: {} date: {}'.format(full_path, title, date)
                raise ValueError(error_text)
    
    return (all_topics, processed_posts)



