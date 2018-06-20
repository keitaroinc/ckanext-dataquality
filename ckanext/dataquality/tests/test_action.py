import requests
import json
import nose

import ckan.logic as l
from ckan.tests import helpers, factories
from ckan import plugins

from ckanext.dataquality.tests.helpers import (
    datastore_create_mock,
    datastore_upsert_mock
)


class ActionBase(object):
    @classmethod
    def setup_class(self):
        self.site_url = 'http://localhost:5000'

        if not plugins.plugin_loaded('dataquality'):
            plugins.load('dataquality')
        if not plugins.plugin_loaded('datastore'):
            plugins.load('datastore')

    def setup(self):
        helpers.reset_db()

    @classmethod
    def teardown_class(self):
        if plugins.plugin_loaded('dataquality'):
            plugins.unload('dataquality')
        if plugins.plugin_loaded('datastore'):
            plugins.unload('datastore')


class TestDatastoreActions(ActionBase):
    @nose.tools.raises(l.NotAuthorized)
    def test_datastore_create(self):
        helpers.call_action('datastore_create', {})

    @nose.tools.raises(l.NotAuthorized)
    def test_datastore_upsert(self):
        helpers.call_action('datastore_upsert', {})

    def test_custom_datastore_create_with_resource(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        organization = factories.Organization()

        with open('ckanext/dataquality/tests/test_create_dataset.json') as data_file:
            kwargs = json.load(data_file)

        kwargs['owner_org'] = organization.get('name')

        dataset = helpers.call_action('package_create',
                                      context=context,
                                      **kwargs)

        data_dict = datastore_create_mock(valid=False)
        data_dict['resource'] = {
            'package_id': dataset['name'],
            'validation': '1'
        }

        result = helpers.call_action('custom_datastore_create',
                                     context=context, **data_dict)

        assert 'validation_report' in result

        data_dict = datastore_create_mock(valid=False)
        data_dict['resource'] = {
            'package_id': dataset['name'],
            'validation': 'enforce'
        }

        result = helpers.call_action('custom_datastore_create',
                                     context=context, **data_dict)

        assert 'validation_report' in result
        assert result['message'] == \
               'Resource cannot be inserted in Datastore due to errors.'

    def test_custom_datastore_upsert(self):
        factories.Organization(name='test-ndk')

        data_dict = datastore_create_mock(valid=True)

        user = factories.Sysadmin()
        context = {'user': user['name']}
        organization = factories.Organization()

        with open('ckanext/dataquality/tests/test_create_dataset.json') as data_file:
            kwargs = json.load(data_file)

        kwargs['owner_org'] = organization.get('name')

        dataset = helpers.call_action('package_create',
                                      context=context,
                                      **kwargs)

        data_dict['resource'] = {
            'package_id': dataset['name'],
            'validation': '1'
        }

        context = {'user': 'default'}

        result = helpers.call_action('custom_datastore_create',
                                     context=context, **data_dict)

        resource_id = result['result']['resource_id']

        data_dict = datastore_upsert_mock()
        data_dict['resource_id'] = resource_id

        result = helpers.call_action('custom_datastore_upsert',
                                     context=context, **data_dict)

        assert 'validation_report' in result

        data_dict = {
            'id': resource_id,
            'validation': 'enforce'
        }

        result = helpers.call_action('resource_patch',
                                     context=context, **data_dict)

        data_dict = datastore_upsert_mock()
        data_dict['resource_id'] = resource_id

        result = helpers.call_action('custom_datastore_upsert',
                                     context=context, **data_dict)

        assert 'validation_report' in result
        assert result['message'] == \
               'Resource cannot be inserted in Datastore due to errors.'
