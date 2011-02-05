from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.query import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from order import managers
from order import models as order_models

csrf_protect_m = method_decorator(csrf_protect)

def create_order_classes(related_class, order_field_names):
    """
    Create order model and admin class. 
    Add order model to order.models module and register admin class.
    Connect ordered_objects manager to related model.
    """
    # Resolve labels for related class.
    labels = resolve_labels(related_class)
            
    # Dynamic Classes
    class OrderItemBase(models.Model):
        """
        Dynamic order class base.
        """
        item = models.ForeignKey(related_class)
        timestamp = models.DateTimeField(auto_now=True)
    
        class Meta:
            abstract = True
            app_label = 'order'
   
    class Admin(admin.ModelAdmin):
        """
        Dynamic order admin class.
        """
        list_display = ('item_link',) + tuple(order_field_names)
        list_editable = order_field_names

        def get_model_perms(self, request):
            """
            Return empty perms dict thus hiding the model from admin index.
            """
            return {}
    
        @csrf_protect_m
        def changelist_view(self, request, extra_context=None):
            list_url = reverse('admin:%s_%s_changelist' % (labels['app'], labels['model'].lower()))
            add_url = reverse('admin:%s_%s_add' % (labels['app'], labels['model'].lower()))

            result = super(Admin, self).changelist_view(request, extra_context={
                'add_url': add_url,
                'list_url': list_url,
                'related_opts': related_class._meta,
            })

            # XXX: Sanitize order on list save.
            #if (request.method == "POST" and self.list_editable and '_save' in request.POST):
            #    sanitize_order(self.model)
            return result

        def item_link(self, obj):
            url = reverse('admin:%s_%s_change' % (labels['app'], labels['model'].lower()), args=(obj.item.id,))
            return '<a href="%s">%s</a>' % (url, obj.item.title)
        item_link.allow_tags = True
        item_link.short_description = 'Item'
    
    # Set up a dictionary to simulate declarations within a class. 
    attrs = {
        '__module__': 'order.models', 
    }
    
    # Create provided order fields and add to attrs.
    fields = {}
    for field in order_field_names:
        fields[field] = models.IntegerField()
    attrs.update(fields)

    # Create the class which automatically triggers Django model processing.
    order_item_class_name = resolve_order_item_class_name(related_class)
    model = type(order_item_class_name, (OrderItemBase, ), attrs)

    # Set the model as part of the order.models module.
    setattr(order_models, order_item_class_name, model)
            
    # Register admin model.
    admin.site.register(model, Admin)
        
    # Add user_order_by method to base QuerySet.
    setattr(QuerySet, 'user_order_by', managers.user_order_by)

    # Return created model class.
    return model

def is_orderable(cls):
    """
    Checks if the provided class is specified as an orderable in settings.ORDERABLE_MODELS.
    If it is return its settings.
    """
    labels = resolve_labels(cls)
    if settings.ORDERABLE_MODELS.has_key(labels['app_model']):
        return settings.ORDERABLE_MODELS[labels['app_model']]
    if settings.ORDERABLE_MODELS.has_key(labels['module_app_model']):
        return settings.ORDERABLE_MODELS[labels['module_app_model']]
    return False

def resolve_labels(cls):
    """
    Returns app, model, app_model, module_app and module_app_model labels for provided class.
    XXX: There has to be a better way to do this.
    """
    labels = {}

    # Resolve module.app label.
    labels['module_app'] = cls.__module__.replace('.models', '')

    # Resolve app label.
    labels['app'] = '.'.join(labels['module_app'].split('.')[1:])

    # Resolve model label
    labels['model'] = cls._meta.object_name

    # Resolve module_app_model label.
    labels['app_model'] = '%s.%s' % (labels['app'], labels['model'])
    
    # Resolve module_app_model label.
    labels['module_app_model'] = '%s.%s' % (labels['module_app'], labels['model'])

    return labels

def resolve_order_item_class_name(cls):
    """
    Returns an OrderItem class name for provided class.
    """
    return '%sOrderItem' % cls._meta.object_name

def resolve_order_item_related_set_name(cls):
    """
    Returns a reverse relation manager name to order items for class.
    """
    return ('%s_set' % resolve_order_item_class_name(cls)).lower()

def sanitize_order(model):
    """
    Sanitize order values so eliminate conflicts and gaps.
    XXX: Early start, very ugly, needs work.
    """
    to_order_dict = {}

    order_field_names = []
    for field in model._meta.fields:
        if isinstance(field, models.IntegerField):
            order_field_names.append(field.name)
    
    for field_name in order_field_names:
        to_order_dict[field_name] = list(model.objects.all().order_by(field_name, '-timestamp'))

    updates = {}
    for field_name, object_list in to_order_dict.items():
        for i, obj in enumerate(object_list):
            position = i + 1
            if getattr(obj, field_name) != position:
                if updates.has_key(obj):
                    updates[obj][field_name] = position
                else:    
                    updates[obj] = {field_name: position}

    for obj, fields in updates.items():
        for field, value in fields.items():
            setattr(obj, field, value)
        obj.save()
