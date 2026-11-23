import os

from django.core.exceptions import ImproperlyConfigured
from django.db import connections
from django.test.runner import DiscoverRunner


class IsolatedDatabaseTestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        for alias in connections:
            connection = connections[alias]
            test_name = connection.settings_dict.get('TEST', {}).get('NAME')
            database_name = connection.settings_dict['NAME']
            if not test_name:
                continue

            if connection.vendor == 'sqlite' and database_name != ':memory:' and test_name != ':memory:':
                same_database = os.path.realpath(os.fspath(database_name)) == os.path.realpath(
                    os.fspath(test_name)
                )
            else:
                same_database = str(database_name) == str(test_name)

            if same_database:
                raise ImproperlyConfigured(
                    'Tests cannot use the configured application database as their test database.'
                )

        return super().setup_databases(**kwargs)
