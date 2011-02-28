from django.conf import settings

from order.utils import create_order_classes

for label, fields in settings.ORDERABLE_MODELS.items():
    create_order_classes(label, fields)
