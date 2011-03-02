import sys
from django.conf import settings

if not settings.configured:
    settings.configure(
        SITE_ID=0,
        DATABASE_ENGINE='sqlite3',
        INSTALLED_APPS=[
            'django.contrib.sites',
            'django.contrib.admin',
            'order',
        ],
        ORDERABLE_MODELS = {
            'sites.Site': ('ordering_field_1', 'ordering_field_2'),
        }
    )

from django.test.simple import run_tests

def runtests(*test_args):
    failures = run_tests(test_args, verbosity=1, interactive=True)
    sys.exit(failures)

if __name__ == '__main__':
    runtests(*sys.argv[1:])
