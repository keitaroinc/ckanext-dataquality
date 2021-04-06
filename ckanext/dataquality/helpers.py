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

from ckan.plugins.toolkit import get_action
from ckan.logic import NotFound


def should_validate_resource(data_dict):
    try:
        resource = data_dict['resource']
        validation = resource['validation']

        if validation in ['1', 'enforce']:
            return validation
    except (KeyError, TypeError):
        try:
            resource_id = data_dict['resource_id']

            try:
                result = get_action('resource_show')(None, {'id': resource_id})
            except NotFound:
                return False

            validation = result['validation']

            if validation in ['1', 'enforce']:
                return validation
        except KeyError:
            return False
