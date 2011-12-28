__author__ = 'KMihajlov'
#{%block imports%}
from google.appengine.ext.db.djangoforms import ModelForm
from django.forms import Form, BaseForm, fields, widgets
from django.forms.extras import widgets as extras
from models.cmsModels import *
#{%endblock%}

class CMSContentForm(Form):
    def __init__(self, *args, **kwargs):
        super(CMSContentForm, self).__init__(*args, **kwargs)
    Title = fields.CharField(required=True, widget=widgets.TextInput(attrs={'style':'width:500px;'}))
    Content = fields.CharField(widget=widgets.Textarea(), required=True)
    Tags = fields.CharField(required=False, widget=widgets.TextInput(attrs={'style':'width:500px;'}))
##End Comment

class CMSMenuForm(Form):
    def __init__(self, *args, **kwargs):
        super(CMSMenuForm, self).__init__(*args, **kwargs)
    key = fields.Field(widget=widgets.HiddenInput, required=False)
    Name = fields.CharField(required=True, min_length=3)
    