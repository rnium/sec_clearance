from django.apps import AppConfig
from django.apps import apps


def get_model_by_name(modelname):
    try:
        model = apps.get_model(app_label='clearance', model_name=modelname)
        return model
    except LookupError:
        return None

class ClearanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clearance'
