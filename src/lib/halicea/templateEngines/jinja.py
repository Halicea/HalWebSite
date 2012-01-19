from conf.settings import VIEWS_DIR
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader(VIEWS_DIR))

def render(self, template, dict, debug=False):
    template = env.get_template(template)
    return template.render(dict)