from django.db import models

class OrderedManager(models.Manager):
    """
    Ordered object manager adding order fields to queryset. 
    """
    def get_query_set(self):
        # Get ordering model.
        orderitem_set = resolve_order_item_related_set_name(self.model)
        order_model = orderitem_set.model

        # Resolve ordering model table name.
        db_table = order_model._meta.db_table

        # Add each Integer field on ordering model as extra queryset fields.
        pk_name = self.model._meta.pk.attname
        extra_select = {}
        for field in order_model._meta.fields:
            if isinstance(field, models.IntegerField):
                extra_select[field.name] = '(SELECT %s from %s WHERE item_id=%s.%s)' % (field.name, db_table, self.model._meta.db_table, pk_name)

        return super(OrderedManager, self).get_query_set().extra(select=extra_select)
