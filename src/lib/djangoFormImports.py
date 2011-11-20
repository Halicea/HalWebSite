import django
if django.VERSION[0]>=1:
    from django.forms import fields, widgets, extras, BaseForm
else:
    from django.newforms import fields, widgets, extras, BaseForm