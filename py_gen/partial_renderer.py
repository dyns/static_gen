from jinja2 import Template

# generate partial
def gen(partial_html, injects):
    template = Template(partial_html)
    rendered = template.render(**injects)
    return rendered

