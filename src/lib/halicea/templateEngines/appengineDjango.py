import os
os.environ['DJANGO_SETTINGS_MODULE']  = 'conf.settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template as tmpl
from django.conf import settings
#forse reset django settings 
settings._target=None 
#register filters and tags
tmpl.register_template_library('lib.customFilters')
def render(template_path, template_dict, debug):
    return tmpl.render(template_path, template_dict, debug)