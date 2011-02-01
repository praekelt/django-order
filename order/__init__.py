from django.conf import settings
from django.db.models.signals import class_prepared

import order.models

def create_model(name, order_field_names, relation):
    """
    Create model and register with admin.
    """
    
    from django.db import models
    from django.contrib import admin
    
    class Meta:
        app_label = 'order'
   
    # Set up a dictionary to simulate declarations within a class 
    attrs = {
        '__module__': 'order.models', 
        'Meta': Meta
    }

    # Create various order fields.
    fields = {
        'item': models.ForeignKey('tube.AdactusClip')
    }
    for field in order_field_names:
        fields[field] = models.IntegerField()

    # Add in order fields.
    if fields:
        attrs.update(fields)

    # Create the class, which automatically triggers ModelBase processing.
    model = type(name, (models.Model,), attrs)

    # Set the model as part of order.models.
    setattr(order.models, name, model)
    
    # Create an Admin class and register it with admin.
    class Admin(admin.ModelAdmin):
        list_display = ['item',] + order_field_names
    
    admin.site.register(model, Admin)
    
    # Return created model class.
    return model

previous_sender = None
def create_order_models(sender, **kwargs):
    global previous_sender

    # XXX: Nasty jugling, clean this up.
    temp = previous_sender
    previous_sender = sender
    sender = temp
    
    if not sender:
        return 

    modules = settings.ORDERABLE_MODELS.keys()
    # XXX: There has to be a better way to do this.
    app_model = ('%s.%s' % (sender.__module__, sender._meta.object_name)).replace('.models', '')
    if app_model in modules:
        model = create_model('%sOrderItem' % app_model.split('.')[-1], order_field_names=['home', 'videos'], relation=app_model)
    
class_prepared.connect(create_order_models)
