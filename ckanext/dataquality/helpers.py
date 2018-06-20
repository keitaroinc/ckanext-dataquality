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
