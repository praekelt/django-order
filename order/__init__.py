from django.db.models.signals import post_save

from order import signal_handlers

post_save.connect(signal_handlers.post_save)
