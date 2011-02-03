from arrange.utils import create_arrange_classes, is_arrangeable, resolve_labels, resolve_arrange_item_related_set_name, sanitize_arrangement

previous_sender = None
def class_prepared(sender, **kwargs):
    """
    On class prepare create arrange model with specified arrangement fields and admin class for arrangeable models.
    """
    # Seems like sender isn't fully admin registered here, so we do a silly previous sender dance.
    # XXX: Sender to get signalled last will probably not get an arrange model, fix.
    global previous_sender
    original_previous_sender = previous_sender
    previous_sender = sender
    sender = original_previous_sender
    if not sender:
        return 

    # Only create arrange models for those modules specified in settings.
    arrange_field_names = is_arrangeable(sender)
    if arrange_field_names:
        create_arrange_classes(related_class=sender, arrange_field_names=arrange_field_names)

def post_save(sender, instance, created, **kwargs):
    """
    After save create arrange instance for sending instance for arrangeable models.
    """
    # Only create arrange model instances for those modules specified in settings.
    arrange_field_names = is_arrangeable(sender)
    if arrange_field_names:
        arrangeitem_set = getattr(instance, resolve_arrange_item_related_set_name(sender))
        if not arrangeitem_set.all():
            fields = {}
            for arrange_field_name in arrange_field_names:
                fields[arrange_field_name] = 1
            arrangeitem_set.model.objects.create(item=instance, **fields)
            sanitize_arrangement(arrangeitem_set.model)
