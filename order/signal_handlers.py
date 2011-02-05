from order.utils import create_order_classes, is_orderable, resolve_labels, resolve_order_item_related_set_name, sanitize_order

previous_sender = None
def class_prepared(sender, **kwargs):
    """
    On class prepare create order model with specified order fields and admin class for orderable models.
    """
    # Seems like sender isn't fully admin registered here, so we do a silly previous sender dance.
    # XXX: Sender to get signalled last will probably not get an order model, fix.
    global previous_sender
    original_previous_sender = previous_sender
    previous_sender = sender
    sender = original_previous_sender
    if not sender:
        return 

    # Only create order models for those modules specified in settings.
    order_field_names = is_orderable(sender)
    if order_field_names:
        create_order_classes(related_class=sender, order_field_names=order_field_names)

def post_save(sender, instance, created, **kwargs):
    """
    After save create order instance for sending instance for orderable models.
    """
    # Only create order model instances for those modules specified in settings.
    order_field_names = is_orderable(sender)
    if order_field_names:
        orderitem_set = getattr(instance, resolve_order_item_related_set_name(sender))
        if not orderitem_set.all():
            fields = {}
            for order_field_name in order_field_names:
                fields[order_field_name] = 1
            orderitem_set.model.objects.create(item=instance, **fields)
            sanitize_order(orderitem_set.model)
