Static site generator written in Python3

python3 -m mygen config_path 


commands:
build
build_serve
new_post name


------------

create a virtual env
activate

1) install static generator:
	do pip install -e my_gen_path

2) create a default configuration file using:
	my_gen default-config --path path [default: ./config.yaml]

3) copy the default template content folder

4) execute generator with config as paramater:
	my_gen config

create a post:
	my_gen new-post post_title

add pages by adding page_name.md files to the pages_folder folder set in the config. For example, in the config, if pages_folder: './content/pages', to add a page at my_site.com/my_page.html, add the file my_page.md to ./content/pages.

copy the default template:
	my_gen copy_default_template_to path

There is an archive_template, pages_template, post_template.html, post_template.md which is injected to the post_template.html, and topic_template. In html templates, you can inject partials using the {{ partial_name }} syntax. You must place the partials in the partials folder defined in the config. 


build and serve the site:
	my_gen build-serve

you can push the generated site to a static hosting service or a service like github for github pages.

other features
 posts are formatted in markdown which means you can also include html in your posts
 you can embed youtube links, vimeo links in markdown posts with the syntax: 

------

todo:

inflate html by attemping to inflate a template, reading all depdencies, generating DAG if possible, walking through graph and inflating template to html, inflate all the way down to main entry. Cache where possible, and continue until all templates are inflated.

move the generation logic out of the generator itself and into the templates. So the archive_template.html could have embeded python: 
{ for post in posts}
{{post.date}}
{{post.post_content}}
{}

include some kind of css templating system

load templates by reading files 
