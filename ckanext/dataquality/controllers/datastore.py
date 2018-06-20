import json

import ckan.lib.base as base
import ckan.logic as l


class DatastoreController(base.BaseController):

    def prevent_access(self):
        raise l.NotAuthorized('Access denied: This action cannot be used')
