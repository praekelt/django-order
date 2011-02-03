from django.contrib import admin

from arrange.utils import is_arrangeable

# Set change_list_template on arrangeable models' admin classes to user the arrange_change_list template, thus enabling 'Arrange' tool.
for model, model_admin in admin.site._registry.items():
    if is_arrangeable(model):
        model_admin.change_list_template = 'arrange/arrange_change_list.html'
