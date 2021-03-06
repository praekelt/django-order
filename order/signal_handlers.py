from order.utils import create_order_objects, is_orderable, resolve_labels, \
        resolve_order_item_related_set_name, sanitize_order


def post_save(sender, instance, created, **kwargs):
    """
    After save create order instance for sending instance for orderable models.
    """
    # Only create order model instances for
    # those modules specified in settings.
    model_label = '.'.join([sender._meta.app_label, sender._meta.object_name])
    labels = resolve_labels(model_label)

    order_field_names = is_orderable(model_label)
    if order_field_names:
        orderitem_set = getattr(
            instance,
            resolve_order_item_related_set_name(labels)
        )
        if not orderitem_set.all():
            fields = {}
            for order_field_name in order_field_names:
                fields[order_field_name] = 1
            orderitem_set.model.objects.create(item=instance, **fields)
            sanitize_order(orderitem_set.model)


def post_syncdb(sender, created_models, **kwargs):
    for model in created_models:
        label = '.'.join([model._meta.app_label, model._meta.object_name])
        order_fields = is_orderable(label)
        if order_fields:
            create_order_objects(model, order_fields)
