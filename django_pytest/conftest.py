import os, sys
sys.path.append('.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
from django.test.client import Client
from django.test.utils import setup_test_environment, teardown_test_environment
from django.core.management import call_command
from django.core import mail

from django.contrib.auth.models import User


def pytest_funcarg__django_client(request):
    '''py.test funcargs are awesome. This ugly function basically creates a
    test environment with an empty database every time you write a test
    function that accepts an argument named 'django_client.' Most of the time
    you won't use this, you'll use the 'client' funcarg below instead. This
    funcarg is only reset once per test session. The 'client' funcarg empties
    the database after each test to ensure a clean slate.'''
    old_name = settings.DATABASE_NAME
    def setup():
        setup_test_environment()
        settings.DEBUG = False
        from django.db import connection
        connection.creation.create_test_db(1, True)
        return Client()
    def teardown(client):
        teardown_test_environment()
        from django.db import connection
        connection.creation.destroy_test_db(old_name, 1)
    return request.cached_setup(setup, teardown, "session")

def pytest_funcarg__client(request):
    '''Creates a test environment using the 'django_client' funcarg above, but
    also ensures the database is flushed after running each test.'''
    def setup():
        return request.getfuncargvalue('django_client')
    def teardown(client):
        call_command('flush', verbosity=0, interactive=False)
        mail.outbox = []
    return request.cached_setup(setup, teardown, "function")

# Note: I make test usernames and passwords identical for easy login
def pytest_funcarg__user(request):
    '''Create a user with no special permissions.'''
    user = User.objects.create_user(username="user", password="user", email="user@example.com")
    return user

def pytest_funcarg__admin(request):
    '''Create an admin user with all permissions.'''
    admin = User.objects.create_user(username="admin", password="admin", email="admin@example.com")
    admin.is_superuser = True
    admin.save()
    return admin
