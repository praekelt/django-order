from django.contrib import admin
from django.http import HttpResponseRedirect

import object_tools

from order.utils import is_orderable


class Order(object_tools.ObjectTool):
    name = 'order'
    label = 'Order'

    def view(self, request, extra_context=None):
        return HttpResponseRedirect('/admin/order/%sorderitem/' % \
                extra_context['opts'].object_name.lower())

for model, model_admin in admin.site._registry.items():
    label = '.'.join([model._meta.app_label, model._meta.object_name])
    if is_orderable(label):
        object_tools.tools.register(Order, model)
