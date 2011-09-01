DATABASE_ENGINE='sqlite3'

SITE_ID = 0

INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.admin',
    'order',
]

ORDERABLE_MODELS = {
    'sites.Site': ('ordering_field_1', 'ordering_field_2'),
}
