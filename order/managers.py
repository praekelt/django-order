import order

def user_order_by(self, field):
    """
    Queryset method ordering objects by user ordering field.
    """
    # Get ordering model.
    orderitem_set = getattr(self.model, order.utils.resolve_order_item_related_set_name(self.model))
    order_model = orderitem_set.related.model
    
    # Resolve ordering model table name.
    db_table = order_model._meta.db_table
    
    # Add ordering field as extra queryset fields.
    pk_name = self.model._meta.pk.attname
    extra_select = {
        field: '(SELECT %s from %s WHERE item_id=%s.%s)' % (field, db_table, self.model._meta.db_table, pk_name)
    }
    return self.extra(select=extra_select).order_by(field)

