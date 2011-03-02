from unittest import TestCase

from django.conf import settings
from django.db.models import get_models
from django.db.models.fields import IntegerField
from order import models

class ManagerTestCase(TestCase):
    def test_user_order_by(self):
        # Resolve ordering models and field names.
        order_model = get_models(models)[0]
        ordered_model = order_model.item.field.rel.to
       
        field_names = []
        for field in order_model._meta.fields:
            if field.__class__ == IntegerField:
                field_names.append(field.name)
            
        # Create some ordered models.
        for i in range(1, 10):
            ordered_model.objects.get_or_create(id=i)
        
        # We should now have an order model item for each created object
        order_model_items = [obj.item for obj in order_model.objects.all()]
        for obj in ordered_model.objects.all():
            self.failUnless(obj in order_model_items)
        
        # Confirm user_order_by method is available on queryset.
        self.failUnless(ordered_model.objects.all().user_order_by)

        # Test user_order_by for each field name.
        for field_name in field_names:
        
            # Default behaviour is to sort ascending.
            asc_objects = ordered_model.objects.all().user_order_by(field_name)
            asc_ids = [obj.item.id for obj in order_model.objects.all().order_by(field_name)]
            for i, obj in enumerate(asc_objects):
                self.failUnless(obj.id == asc_ids[i])
        
            # Descedning is achieved by adding '-' to field name.
            desc_objects = ordered_model.objects.all().user_order_by('-%s' % field_name)
            desc_ids = [obj.item.id for obj in order_model.objects.all().order_by('-%s' % field_name)]
            for i, obj in enumerate(desc_objects):
                self.failUnless(obj.id == desc_ids[i])

class ModelsTestCase(TestCase):
    def test_model_creation(self):
        """
        Tests whether appropriate OrderItem models have been created 
        for models defined in ORDERABLE_MODELS setting.
        """
        orderable_models = [key.split('.')[-1] for key in settings.ORDERABLE_MODELS.keys()]
        for model in get_models(models):
            model_name = model._meta.object_name.replace('OrderItem', '')
            self.failUnless(model_name in orderable_models, 'OrderItem model for %s not created.' % model_name)
