import order

def user_order_by(self, field):
    """
    Queryset method ordering objects by user ordering field.
    """
    # Get ordering model.
    model_label = order.utils.resolve_labels('.'.join([self.model._meta.app_label, self.model._meta.object_name]))
    orderitem_set = getattr(self.model, order.utils.resolve_order_item_related_set_name(model_label))
    order_model = orderitem_set.related.model

    # Resolve ordering model table name.
    db_table = order_model._meta.db_table

    # Add ordering field as extra queryset fields.
    pk_name = self.model._meta.pk.attname

    # If we have a descending query remove '-' from field name when quering.
    sanitized_field = field.lstrip('-')

    extra_select = {
        sanitized_field: '(SELECT %s from %s WHERE item_id=%s.%s)' % (sanitized_field, db_table, self.model._meta.db_table, pk_name)
    }

    # Use original field name when ordering to allow for descending.
    return self.extra(select=extra_select).all().order_by(field)

