# -*- coding: utf-8 -*-

import os
from os.path import join
#from lib.halicea import deCMSPageControllerfaultControllerMethods as dcm
DEBUG = True
TEMPLATE_DEBUG = True
DEFAULT_CHARSET ='UTF-8'
from lib.halicea import dummyControllerMethods as dcm
APPENGINE_PATH = '/home/costa/DevApps/google_appengine'
if os.name == 'nt':
    APPENGINE_PATH = '/home/costa/DevApps/google_appengine'
    #APPENGINE_PATH = 'C:\\devApps\\google_appengine'

#we define the path relatively to our settings file
PROJ_LOC = os.path.dirname(os.path.dirname(__file__))

#MVC Directories
MODELS_DIR = join(PROJ_LOC,'Models')
VIEWS_DIR = join(PROJ_LOC,'Views')
VIEWS_RELATIVE_DIR = 'Views'
FORM_MODELS_DIR = join(PROJ_LOC, 'Forms')
CONTROLLERS_DIR = join(PROJ_LOC, 'Controllers')
BASE_VIEWS_DIR = join(VIEWS_DIR, 'bases')
BLOCK_VIEWS_DIR = join(VIEWS_DIR, 'blocks')
PAGE_VIEWS_DIR = join(VIEWS_DIR, 'pages')
FORM_VIEWS_DIR = join(VIEWS_DIR, 'forms')
STATIC_DATA_DIR = join(PROJ_LOC, 'StaticData')
JSCRIPTS_DIR = join(STATIC_DATA_DIR, 'jscripts')
IMAGES_DIR = join(STATIC_DATA_DIR, 'images')
STYLES_DIR = join(STATIC_DATA_DIR, 'styles')
HANDLER_MAP_FILE = join(PROJ_LOC, 'handlerMap.py')
#End MVC Directories

#MVC Sufixes
MODEL_MODULE_SUFIX = 'Models'
MODEL_FORM_MODULE_SUFIX = 'Forms'
CONTROLLER_MODULE_SUFIX = 'Controllers'
MODEL_CLASS_SUFIX = ''
MODEL_FORM_CLASS_SUFIX = 'Form'
CONTROLLER_CLASS_SUFIX = 'Controller'
BASE_VIEW_SUFIX = ''
PAGE_VIEW_SUFFIX = ''
FORM_VIEW_SUFFIX = 'Form'
BLOCK_VIEW_SUFIX = ''
BASE_MOBILE_VIEW_EXTENSION = '_mobile'
#End MVC Sufixes
#File Extensions
CONTROLLER_EXTENSTION = '.py'
MODEL_EXTENSTION = '.py'
MODEL_FORM_EXTENSTION = '.py'
VIEW_EXTENSTION = '.html'

template_debug=True
show_errors = True
MagicLevel = 3

DEFAULT_OPERATIONS = {
                      'default':{'method':dcm.index, 'view':False},
                      'index':{'method':dcm.index, 'view':True}, 
                      'details':{'method':dcm.details, 'view':True},
                      'edit':{'method':dcm.edit, 'view':True},
                      'insert':{'method':dcm.save, 'view':False},
                      'update':{'method':dcm.save, 'view':False},
                      'delete':{'method':dcm.delete, 'view':False},
                     }

#DJANGO APP SETTINGS SECTION
TEMPLATE_DIRS = (VIEWS_DIR,)
ROOT_URLCONF ='handlerMap'
TEMPLATE_LOADERS = ('lib.halicea.HalTemplateLoader.HalLoader','django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader')

#PASTE YOUR CONFIGURATION HERE
USE_I18N = True
#LANGUAGES = (
#    # 'en', 'zh_TW' match the directories in conf/locale/*
#    ('en', _('English')),
#    ('mk_MK', _('Macedonian')),
#    ('ro_RO', _('Romanian')),
#    )
COOKIE_KEY = '''2zÆœ;¾±þ”¡j:ÁõkçŸÐ÷8{»Ën¿A—jÎžQAQqõ"bøó÷*%†™ù¹b¦$vš¡¾4ÇŸ^ñ5¦'''