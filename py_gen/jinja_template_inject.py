from jinja2 import Template

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


