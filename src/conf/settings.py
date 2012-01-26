# -*- coding: utf-8 -*-
import os
from os.path import join
PLATFORM = 'appengine'
DEBUG = False
TEMPLATE_DEBUG = DEBUG
DEFAULT_CHARSET ='UTF-8'

DEFAULT_OPERATIONS =\
  {
  'default':{'method':'lib.halicea.dummyControllerMethods.index', 'view':False},
  'index':{'method':'lib.halicea.dummyControllerMethods.index', 'view':True}, 
  'view':{'method':'lib.halicea.dummyControllerMethods.view', 'view':True},
  'edit':{'method':'lib.halicea.dummyControllerMethods.edit', 'view':True},
  'new':{'method': 'lib.halicea.dummyControllerMethods.edit', 'view':False},
  'save':{'method':'lib.halicea.dummyControllerMethods.save', 'view':False},
  'delete':{'method':'lib.halicea.dummyControllerMethods.delete', 'view':False},
   }

PLUGINS =\
  [
   ("Links", 'controllers.cmsControllers.CMSLinksController'),
   ("Contents", 'controllers.cmsControllers.CMSContentController'),
   ("Menus", 'controllers.cmsControllers.MenuController'),
  ]

EXTENSIONS =\
   [
  'lib.halicea.extensions.AuthenticationMixin',
  'lib.halicea.extensions.HtmlMixin'
   ]

APPENGINE_PATH = '/home/costa/DevApps/google_appengine'
if os.name == 'nt':
  APPENGINE_PATH = '/home/costa/DevApps/google_appengine'
  #APPENGINE_PATH = 'C:\\devApps\\google_appengine'

#we define the path relatively to our settings file
PROJ_LOC = os.path.dirname(os.path.dirname(__file__))

#MVC Directories  
#!--DO NOT CHANGE THIS UNLESS YOU KNOW WHAT YOU ARE DOING--!
MODELS_DIR = join(PROJ_LOC,'models')
VIEWS_DIR = join(PROJ_LOC,'views')
VIEWS_RELATIVE_DIR = 'views'
FORM_MODELS_DIR = join(PROJ_LOC, 'forms')
CONTROLLERS_DIR = join(PROJ_LOC, 'controllers')
BASE_VIEWS_DIR = join(VIEWS_DIR, 'bases')
BLOCK_VIEWS_DIR = join(VIEWS_DIR, 'blocks')
PAGE_VIEWS_DIR = join(VIEWS_DIR, 'pages')
FORM_VIEWS_DIR = join(VIEWS_DIR, 'forms')
STATIC_DATA_DIR = join(PROJ_LOC, 'static_data')
JSCRIPTS_DIR = join(STATIC_DATA_DIR, 'jscripts')
IMAGES_DIR = join(STATIC_DATA_DIR, 'images')
STYLES_DIR = join(STATIC_DATA_DIR, 'styles')
HANDLER_MAP_FILE = join(PROJ_LOC, 'handlerMap.py')
TESTS_DIR = join(PROJ_LOC, 'tests')
DOCS_DIR = join(PROJ_LOC, 'docs')
APPS_DIR = join(PROJ_LOC, 'apps')
LIB_DIR = join(PROJ_LOC, 'lib')
REPOS_DIR = join(PROJ_LOC, 'repositories')
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
MagicLevel = 3


#DJANGO APP SETTINGS SECTION 
#SAME CONFINGURATION IS USED FOR DJANGO 
TEMPLATE_DIRS = (VIEWS_DIR,)
ROOT_URLCONF ='handlerMap'
TEMPLATE_LOADERS = ('lib.halicea.HalTemplateLoader.HalLoader','django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader')

#PASTE YOUR CONFIGURATION HERE
USE_I18N = False
#LANGUAGES = (
#  # 'en', 'zh_TW' match the directories in conf/locale/*
#  ('en', _('English')),
#  ('mk_MK', _('Macedonian')),
#  ('ro_RO', _('Romanian')),
#  )
COOKIE_KEY = '''2zÆœ;¾±þ”¡j:ÁõkçŸÐ÷8{»Ën¿A—jÎžQAQqõ"bøó÷*%†™ù¹b¦$vš¡¾4ÇŸ^ñ5¦'''