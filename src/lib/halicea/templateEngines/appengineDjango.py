import os
os.environ['DJANGO_SETTINGS_MODULE']  = 'conf.settings'
from django.template.loader import get_template
from django.template import Context
from django.template import Library
from lib.customFilters import hash, call

register = Library()

def render(template_path, template_dict, debug):
    t = get_template(template_path)
    return t.render(Context(template_dict))
    
