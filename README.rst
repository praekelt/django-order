Django Order
============
**Django app allowing users to manually order objects via admin.**

Provides an additional *order* tool within admin with which objects can be ordered by any number of arbitrary ``settings`` defined fields. A ``user_order_by`` queryset method allows for retrieval of objects as they were ordered by users via admin. 

**NOTE: Be careful, django-order is under heavy development. Contributions much appreciated.**

.. contents:: Contents
    :depth: 5

Installation
------------

#. Install or add django-order to your Python path.

#. Add ``order`` to your ``INSTALLED_APPS`` setting.
   
   **NOTE: Make sure to add order as the last app in your INSTALLED_APPS setting in order for models and admin templates to be set correctly.**

#. Add an ``ORDERABLE_MODELS`` setting to your project's ``settings.py`` file. This settings is a dictionary containing model-app label strings for those models you want to make orderable as keys. Values take the form of a tupple containing field names on which you want the relevant model to be orderable. I.e. to make the ``User`` model orderable for hypothetical *home* and *users* pages, add the following ``ORDERABLE_MODELS`` setting::

    ORDERABLE_MODELS = {
        'auth.User': ('home', 'users'),
    }

Usage
-----

Admin
~~~~~
Once a model has been registered as orderable an additional *Order* object tool should be visible on the model's change list view.

.. image:: http://cloud.github.com/downloads/praekelt/django-order/django-order-tool.jpg

You can order your items using this tool for each field name specified for you orderable model.

Querysets
~~~~~~~~~

With the ``order`` app installed all queryset objects will have a new ``user_order_by`` method. This method behaves exactly the same as Django's builtin ``order_by`` method except that it expects one of the settings defined field names for the model being queried. It will order the queryset based on the field name you provide. For example, to order users for the *home* page in our hypothetical example you would use the method as follows::

    User.objects.all().user_order_by('home')

