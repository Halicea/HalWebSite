__author__ = 'Costa Halicea'
from django.template.loader import BaseLoader
from django.template import TemplateDoesNotExist
from conf.settings import VIEWS_DIR
import os
class HalLoaderException(Exception):
    def __init__(self, message='Cannot find the template'):
        self.message = message

    def __str__(self):
        return self.message


class HalLoader(BaseLoader):
    def __init__(self, *args, **kwargs):
        self.is_usable = True
        
    def load_template_source(self, template_name, template_dirs=None):
        import warnings
        if os.sep in template_name:
            if os.path.exists(template_name):
                return open(template_name, 'r').read(), template_name
            else:
                raise TemplateDoesNotExist('Template '+template_name+' was not found and was given by absolute path')
        for root, dirs, files in os.walk(VIEWS_DIR):
            for f in files:
                if f == template_name:
                    #warnings.warn('template '+template_name+' was found in '+root)
                    return open(os.path.join(root, f), 'r').read(), f
        raise TemplateDoesNotExist('Template '+template_name+' was not found')

