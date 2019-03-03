Static site generator written in Python3

python3 -m mygen config_path 


commands:
build
build_serve
new_post name


------------

create a virtual env

activate the virtual env

1) install the static generator from local:
	```
	pip install -e my_gen_path
	```

2) create a default configuration file using:
	```
	my_gen copy-default-config --path path [default: ./config.yaml]
	```

5) copy the default content folder with templates and partials and css to the site root, no command to do this, manual copy

6) create a post:
	```
	my_gen new-post post_title --config config_path [default: ./config.yaml]
	```

7) create a page by adding a page_name.md file to the pages directory, default is the content/pages directory.
The page will be available at my_site.com/my_page_name.html
Add the page to navigation bar as a tab: in the config tabs add the name then the url:
	```
	tabs:
  - - 'example page tab name'
    - '/example_page.html' # this can be any url, in this case the relative url to the page
	```

9) build and serve the site:
	```
	my_gen build-serve --config config_path [default: ./config.yaml]
	```

There is an archive_template, pages_template, post_template.html, post_template.md which is injected to the post_template.html, and topic_template. In html templates, you can inject partials using the {{ partial_name }} syntax. You must place the partials in the partials folder defined in the config. 

Adding content to the static directory makes it available at the root. In the static directory there are css files and javascript files.

You can push the generated site to a static hosting service or a service like github for github pages.

other features
 posts are formatted in markdown which means you can also include html in your posts
 you can embed youtube links, vimeo links in markdown posts with the syntax: {{< youtube video_id >}} or {{< vimeo 85040589 >}}

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
