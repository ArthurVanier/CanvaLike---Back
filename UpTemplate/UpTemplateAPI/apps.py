from django.apps import AppConfig


SHAPE_MODEL_LIST = ['circle', 'rectangle', 'text', 'media']


class UptemplateapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'UpTemplateAPI'
    content_types = {}
    

        



