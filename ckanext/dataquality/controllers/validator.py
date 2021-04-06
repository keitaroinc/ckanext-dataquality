"""
ckanext-dataquality
Copyright (c) 2018 Keitaro AB

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
import os

from goodtables import Inspector
from pylons import config

from ckan.plugins.toolkit import get_action
from ckan.logic import NotFound

schema_mapped_types = {
    'text': 'string',
    'int': 'integer',
    'integer': 'integer',
    'float': 'number',
    'bool': 'boolean',
    'boolean': 'boolean',
    'date': 'date',
    'time': 'time',
    'timestamp': 'datetime'
}


class ValidatorController():

    def __init__(self):
        self.schema = {
            'fields': []
        }

    def validate(self, data_dict, action):

        records = data_dict.get('records', None)

        if not records:
            return self.error('records')

        if action == 'datastore_create':
            fields = data_dict.get('fields', None)

            if not fields:
                return self.error('fields')

            for field in fields:
                type = field.get('type', None)
                type = schema_mapped_types.get(type, type)

                field_descriptor = {
                    'name': field.get('id', None),
                    'type': type
                }

                self.schema['fields'].append(field_descriptor)
        elif action == 'datastore_upsert':
            resource_id = data_dict.get('resource_id', None)

            if not resource_id:
                return self.error('resource_id')

            try:
                data_dict = {'id': resource_id}
                result = get_action('datastore_info')(None, data_dict)
                schema = result['schema']

                for field in schema:
                    type = schema[field]
                    type = schema_mapped_types.get(type, type)

                    field_descriptor = {
                        'name': field,
                        'type': type
                    }

                    self.schema['fields'].append(field_descriptor)
            except NotFound:
                return False

        fallback_storage_path = os.path.dirname(os.path.realpath(__file__))
        schema_file = '{0}/{1}'.format(config.get('ckan.storage_path',
                                                  fallback_storage_path),
                                       'schema.json')

        with open(schema_file, 'w') as fp:
            json.dump(self.schema, fp)

        inspector = Inspector(order_fields=True)
        report = inspector.inspect(records, schema=schema_file)

        os.remove(schema_file)

        return report

    def error(self, value):
        message = 'Data validation cannot be performed. '\
            'Missing value: {arg}'.format(arg=value)

        return {
            'error-count': 1,
            'error': {
                'message': message
            }
        }
