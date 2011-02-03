from django.contrib import admin

from order.utils import is_orderable

# Set change_list_template on orderable models' admin classes to user the order_change_list template, thus enabling 'Order' tool.
for model, model_admin in admin.site._registry.items():
    if is_orderable(model):
        model_admin.change_list_template = 'order/order_change_list.html'
