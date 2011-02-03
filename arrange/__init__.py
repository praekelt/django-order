from django.db.models.signals import class_prepared, post_save

from arrange import signal_handlers

class_prepared.connect(signal_handlers.class_prepared)
post_save.connect(signal_handlers.post_save)
