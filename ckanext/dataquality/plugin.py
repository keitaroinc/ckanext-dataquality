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

from ckan import plugins
from ckan.plugins import toolkit

from ckanext.dataquality.logic import action
from ckanext.dataquality.logic.validators import validation_options


class DataqualityPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IDatasetForm)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'dataquality')

    # IRoutes

    def before_map(self, map):
        controller =\
            'ckanext.dataquality.controllers.datastore:DatastoreController'

        map.redirect('/api/action/datastore_create',
                     '/api/3/action/datastore_create')
        map.connect('/api/{ver:1|2|3}/action/datastore_create',
                    controller=controller,
                    action='prevent_access')

        map.redirect('/api/action/datastore_upsert',
                     '/api/3/action/datastore_upsert')
        map.connect('/api/{ver:1|2|3}/action/datastore_upsert',
                    controller=controller,
                    action='prevent_access')

        return map

    # IActions

    def get_actions(self):
        return {
            'custom_datastore_create': action.datastore_create,
            'custom_datastore_upsert': action.datastore_upsert
        }

    # IDatasetForm

    def _modify_package_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')

        schema['resources'].update({
            'validation': [ignore_missing, validation_options]
        })

        return schema

    def create_package_schema(self):
        schema = super(DataqualityPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)

        return schema

    def update_package_schema(self):
        schema = super(DataqualityPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)

        return schema

    def show_package_schema(self):
        schema = super(DataqualityPlugin, self).show_package_schema()

        return schema

    def is_fallback(self):
        return False

    def package_types(self):
        return []
