from django.conf import settings
from django.db.models.signals import class_prepared

import order.models

from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
csrf_protect_m = method_decorator(csrf_protect)

def create_model(name, order_field_names, relation, relation_app_label, relation_model_name, relation_app_model_label):
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
        'item': models.ForeignKey(relation)
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
        list_display = ['item_link',] + order_field_names

        def get_model_perms(self, request):
            """
            Return empty perms dict thus hiding the model from admin index.
            """
            return {}
    
        @csrf_protect_m
        def changelist_view(self, request, extra_context=None):
            from django.core.urlresolvers import reverse
            list_url = reverse('admin:%s_%s_changelist' % (relation_app_label, relation_model_name.lower()))
            add_url = reverse('admin:%s_%s_add' % (relation_app_label, relation_model_name.lower()))

            return super(Admin, self).changelist_view(request, extra_context={
                'add_url': add_url,
                'list_url': list_url,
                'relation_opts': relation._meta,
            })

        def item_link(self, obj):
            from django.core.urlresolvers import reverse
            url = reverse('admin:%s_%s_change' % (relation_app_label, relation_model_name.lower()), args=(obj.id,))
            
            return '<a href="%s">%s</a>' % (url, obj.item.title)
        item_link.allow_tags = True
    
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

    # Compute labels. XXX: There has to be a better way to do this.
    app_label = sender.__module__.replace('.models', '')
    model_name = sender._meta.object_name
    app_model_label = '%s.%s' % (app_label, model_name)
    if app_model_label in modules:
        app_label = '.'.join(app_label.split('.')[1:])
        app_model_label = '%s.%s' % (app_label, model_name)
        model = create_model(
            '%sOrderItem' % model_name, 
            order_field_names=['home', 'videos'], 
            relation=sender,
            relation_app_label=app_label,
            relation_model_name=model_name,
            relation_app_model_label=app_model_label,
        )
    
class_prepared.connect(create_order_models)
