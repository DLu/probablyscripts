import jinja2
import pathlib


def easy_jinja_render(template_path, **kwargs):
    if not isinstance(template_path, pathlib.Path):
        template_path = pathlib.Path(template_path)

    template_loader = jinja2.FileSystemLoader(searchpath=template_path.parent)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_path.name)

    return template.render(**kwargs)
