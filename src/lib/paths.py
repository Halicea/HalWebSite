'''
Created on 04.1.2010

@author: KMihajlov
'''
import os
import os.path as p
from os.path import join as pjoin
import conf.settings as settings
from google.appengine.api import memcache
os.path.sep = '/'
os.pathsep = '/'

def GetTemplateDir(template_type):
    # @type template_type:str
    return p.join(settings.PAGE_VIEWS_DIR, template_type)

def getViewsDict(directory, base=''):
    result = {}
    #memcached for better performance
    memResult = memcache.get('paths_ViewsDict_'+directory)
    if memResult is None:
        if os.path.exists(directory) and os.path.isdir(directory):
            for f in os.listdir(directory):
                rf = os.path.join(directory, f)
                if os.path.isfile(rf):
                    result[f[:f.rindex('.')]] = os.path.abspath(rf)#[base and len(base) or 0:]
        memcache.add(key='paths_ViewsDict', value=result)
        memResult = result
    return memResult

def GetBasesDict():
    result = getViewsDict(settings.BASE_VIEWS_DIR, settings.VIEWS_RELATIVE_DIR)
    return result

def GetBlocksDict():
    result = getViewsDict(settings.BLOCK_VIEWS_DIR, settings.VIEWS_RELATIVE_DIR)
    result.update(__blocksDict__)
    return result

def GetFormsDict(dir):
    result = getViewsDict(p.join(settings.FORM_VIEWS_DIR, dir), settings.VIEWS_RELATIVE_DIR)
    return result

__blocksDict__={
        "blLogin":          pjoin(settings.BLOCK_VIEWS_DIR,'login_menu.inc.html'),
        "mnTopMenu":        pjoin(settings.BLOCK_VIEWS_DIR,'top_menu.inc.html'),
        "mnMainMenu":        pjoin(settings.BLOCK_VIEWS_DIR,'menu.bl.inc.html'),
        ### Menu Blocks
        }

__pluginsDict__={
                 'plQuestionarySmall': {'path': '../../lib/plugins/questionaryPlugin',
                                        'view': 'questionaryView.html',
                                        'controller': '',
                                        },
                 }