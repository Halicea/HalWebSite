import os
from os.path import join as pjoin
import conf.settings

def LocateControllerModule(packageName):
    return pjoin(settings.CONTROLLERS_DIR, BasePathFromName(packageName)+settings.CONTROLLER_MODULE_SUFIX+'.py')
def LocateModelModule(packageName):
    return pjoin(settings.MODELS_DIR, BasePathFromName(packageName)+settings.MODEL_MODULE_SUFIX+'.py')
def LocateFormModelModule(packageName):
    return pjoin(settings.FORM_MODELS_DIR, BasePathFromName(packageName)+settings.MODEL_FORM_MODULE_SUFIX+'.py')

def LocatePagesDir(packageName):
    return pjoin(settings.PAGE_VIEWS_DIR, BasePathFromName(packageName))
def LocateFormsDir(packageName):
    return pjoin(settings.FORM_VIEWS_DIR, BasePathFromName(packageName))
def BasePathFromName(packageName, sep=os.path.sep, splitter='.'):
    return sep.join(packageName.split(splitter))

