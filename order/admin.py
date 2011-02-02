from django.conf import settings
from django.contrib import admin

for model, model_admin in admin.site._registry.items():
    
    modules = settings.ORDERABLE_MODELS.keys()
    
    app_model = ('%s.%s' % (model.__module__, model._meta.object_name)).replace('.models', '')
    
    if app_model in modules:
        model_admin.change_list_template = 'order/order_change_list.html'
