from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.query import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from arrange import managers
from arrange import models as arrange_models

csrf_protect_m = method_decorator(csrf_protect)

def create_arrange_classes(related_class, arrange_field_names):
    """
    Create arrange model and admin class. 
    Add arrange model to arrange.models module and register admin class.
    Connect arrange queryset method to QuerySet
    """
    # Resolve labels for related class.
    labels = resolve_labels(related_class)
            
    # Dynamic Classes
    class ArrangeItemBase(models.Model):
        """
        Dynamic arrange class base.
        """
        item = models.ForeignKey(related_class)
        timestamp = models.DateTimeField(auto_now=True)
    
        class Meta:
            abstract = True
            app_label = 'arrange'
   
    class Admin(admin.ModelAdmin):
        """
        Dynamic arrange admin class.
        """
        list_display = ('item_link',) + tuple(arrange_field_names)
        list_editable = arrange_field_names

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

            # XXX: Sanitize arrangement on list save.
            #if (request.method == "POST" and self.list_editable and '_save' in request.POST):
            #    sanitize_arrangement(self.model)
            return result

        def item_link(self, obj):
            url = reverse('admin:%s_%s_change' % (labels['app'], labels['model'].lower()), args=(obj.item.id,))
            return '<a href="%s">%s</a>' % (url, obj.item.title)
        item_link.allow_tags = True
        item_link.short_description = 'Item'
    
    # Set up a dictionary to simulate declarations within a class. 
    attrs = {
        '__module__': 'arrange.models', 
    }
    
    # Create provided arrange fields and add to attrs.
    fields = {}
    for field in arrange_field_names:
        fields[field] = models.IntegerField()
    attrs.update(fields)

    # Create the class which automatically triggers Django model processing.
    arrange_item_class_name = resolve_arrange_item_class_name(related_class)
    model = type(arrange_item_class_name, (ArrangeItemBase, ), attrs)

    # Set the model as part of the arrange.models module.
    setattr(arrange_models, arrange_item_class_name, model)
            
    # Register admin model.
    admin.site.register(model, Admin)
        
    # Add arrange method to base QuerySet.
    setattr(QuerySet, 'arrange', managers.arrange)

    # Return created model class.
    return model

def is_arrangeable(cls):
    """
    Checks if the provided class is specified as an arrangeable in settings.ARRANGE_MODELS.
    If it is return its settings.
    """
    labels = resolve_labels(cls)
    if settings.ARRANGE_MODELS.has_key(labels['app_model']):
        return settings.ARRANGE_MODELS[labels['app_model']]
    if settings.ARRANGE_MODELS.has_key(labels['module_app_model']):
        return settings.ARRANGE_MODELS[labels['module_app_model']]
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

def resolve_arrange_item_class_name(cls):
    """
    Returns an ArrangeItem class name for provided class.
    """
    return '%sArrangeItem' % cls._meta.object_name

def resolve_arrange_item_related_set_name(cls):
    """
    Returns a reverse relation manager name to arrange items for class.
    """
    return ('%s_set' % resolve_arrange_item_class_name(cls)).lower()

def sanitize_arrangement(model):
    """
    Sanitize arrangement values so eliminate conflicts and gaps.
    XXX: Early start, very ugly, needs work.
    """
    to_arrange_dict = {}

    arrange_field_names = []
    for field in model._meta.fields:
        if isinstance(field, models.IntegerField):
            arrange_field_names.append(field.name)
    
    for field_name in arrange_field_names:
        to_arrange_dict[field_name] = list(model.objects.all().order_by(field_name, '-timestamp'))

    updates = {}
    for field_name, object_list in to_arrange_dict.items():
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
