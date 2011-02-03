import arrange as arrange_module

def arrange(self, field):
    """
    Queryset method arranging items by field.
    """
    # Get arranging model.
    arrangeitem_set = getattr(self.model, arrange_module.utils.resolve_arrange_item_related_set_name(self.model))
    arrange_model = arrangeitem_set.related.model
    
    # Resolve arranging model table name.
    db_table = arrange_model._meta.db_table
    
    # Add arranging field as extra queryset field.
    pk_name = self.model._meta.pk.attname
    extra_select = {
        field: '(SELECT %s from %s WHERE item_id=%s.%s)' % (field, db_table, self.model._meta.db_table, pk_name)
    }
    return self.extra(select=extra_select).order_by(field)

