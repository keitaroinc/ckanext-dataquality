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

import logging

from ckan.plugins.toolkit import get_action
from ckan.logic import check_access, ValidationError

from ckanext.datastore.db import InvalidDataError

from ckanext.dataquality.controllers.validator import ValidatorController
from ckanext.dataquality.helpers import should_validate_resource

log = logging.getLogger(__name__)

def _update_last_modified(context, resource_id):
    from datetime import datetime
    try:
        get_action('resource_patch')(
            context,
            {
                'id': resource_id,
                'last_modified': datetime.utcnow()
            })
    except:
        pass

def datastore_create(context, data_dict):
    ''' Create custom datastore_create action that adds validation on data '''

    return _check_data_validity(context, data_dict, 'datastore_create')


def datastore_upsert(context, data_dict):
    ''' Create custom datastore_upsert action that adds validation on data '''

    return _check_data_validity(context, data_dict, 'datastore_upsert')


def _check_data_validity(context, data_dict, action):
    check_access(action, context, data_dict)

    fields = []

    if action == "datastore_create" and 'resource' in data_dict:
        for field in data_dict['fields']:
            default_field = {}
            default_field['type'] = field['type']
            default_field['id'] = field['id']
            del field['id']
            fields.append(default_field)
        data_dict['resource']['attributes'] = data_dict['fields']
        data_dict['fields'] = fields

    validation = should_validate_resource(data_dict)
    resource_id = data_dict.get('resource_id', '')

    if validation:
        validator = ValidatorController()
        report = validator.validate(data_dict, action)

        if report:
            errors = report.get('error-count', 0)

            if validation == 'enforce' and errors > 0:
                message = 'Resource cannot be inserted in Datastore ' \
                          'due to errors.'

                return {
                    'message': message,
                    'validation_report': report
                }
            else:
                out = {'validation_report': report}
                try:
                    out['result'] = get_action(action)(context, data_dict)
                except (ValidationError, InvalidDataError) as e:
                    if hasattr(e, 'error_dict'):
                        message = e.error_dict
                    elif hasattr(e, 'message'):
                        message = e.message
                    else:
                        message = ''

                    return {
                        'error': message,
                        'validation_report': report
                    }
                else:
                    _update_last_modified(context, resource_id)

                return out

    out = {}
    try:
        out = get_action(action)(context, data_dict)
    except (ValidationError, InvalidDataError) as e:
        raise e
    else:
        _update_last_modified(context, resource_id)

    return out
