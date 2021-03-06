import requests
import copy
import os

class Connectable(object):
    def __init__(self):
        pass
    
class Endpoint(object):
    api_version = "2016-09-01"

    def __init__(self, path):
        self.path = "/"+path

    @property
    def _azure_path(self):
        # TODO: Raise better exception
        return os.environ['AZURE_SEARCH_URL']

    @property
    def _azure_api_key(self):
        return os.environ['AZURE_SEARCH_API_KEY']

    @property
    def _azure_admin_api_key(self):
        return os.environ['AZURE_SEARCH_ADMIN_API_KEY']

    def query_path(self, endpoint):
        if endpoint:
            return self._azure_path+self.path+"/"+endpoint
        return self._azure_path+self.path

    def query_args(self, extra={}):
        x = copy.deepcopy(extra)
        x.update({"api-version": self.api_version})
        return x

    def query_headers(self, needs_admin=False, extra={}):
        x = copy.deepcopy(extra)
        if needs_admin:
            key = self._azure_admin_api_key
        else:
            key = self._azure_api_key
        x.update({"api-key": key})
        return x

    def get(self, data={}, endpoint=None, needs_admin=False):
        return requests.get(
            self.query_path(endpoint),
            params=self.query_args(),
            headers=self.query_headers(needs_admin),
            json = data
        )

    def post(self, data={}, endpoint=None, needs_admin=False):
        return requests.post(
            self.query_path(endpoint),
            params=self.query_args(),
            headers=self.query_headers(needs_admin),
            json = data
        )


    def put(self, data={}, endpoint=None, needs_admin=False):
        return requests.put(
            self.query_path(endpoint),
            params=self.query_args(),
            headers=self.query_headers(needs_admin),
            json = data
        )

    def delete(self, data={}, endpoint=None, needs_admin=False):
        return requests.delete(
            self.query_path(endpoint),
            params=self.query_args(),
            headers=self.query_headers(needs_admin),
            json = data
        )