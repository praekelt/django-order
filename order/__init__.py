from django.db.models.signals import post_save, post_syncdb

from order import models, signal_handlers

post_save.connect(signal_handlers.post_save)
post_syncdb.connect(signal_handlers.post_syncdb, sender=models)
