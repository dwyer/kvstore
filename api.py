# -*-coding:utf-8-*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import contextlib
import json
import urllib
import urllib2


class NotAuthorized(Exception):
    pass


class NotFound(Exception):
    pass


class ApiClient(object):

    BASE_URL = 'http://localhost:8000/api'

    def __init__(self, store=None, token=None):
        self.store = store
        self.token = token

    def __repr__(self):
        return '<%s store=%r token=%r>' % (self.__class__.__name__,
                                           self.store, self.token)

    def new_store(self):
        return self._fetch('/stores', data={})['store']

    def get_store(self):
        return self._fetch('/stores/%s' % self.store)

    def delete_store(self):
        return self._fetch('/stores/%s' % self.store, method='DELETE')

    def new_token(self):
        return self._fetch('/stores/%s/tokens' % (self.store), {})['token']

    def get_tokens(self):
        return self._fetch('/stores/%s/tokens' % (self.store))['tokens']

    def delete_token(self, token):
        return self._fetch('/stores/%s/tokens/%s' % (self.store, token),
                           method='DELETE')

    def get(self, key):
        return self._fetch('/stores/%s/values/%s' % (self.store, key))

    def set(self, key, value):
        return self._fetch('/stores/%s/values/%s' % (self.store, key),
                           data=value)

    def delete(self, key):
        return self._fetch('/stores/%s/values/%s' % (self.store, key),
                           method='DELETE')

    def _fetch(self, path, data=None, method=None):
        url = self.BASE_URL + path
        headers = {}
        if self.token is not None:
            headers['X-Token'] = self.token
        if isinstance(data, dict):
            data = urllib.urlencode(data)
        request = urllib2.Request(url, data=data, headers=headers)
        if method is not None:
            request.get_method = lambda: method
        try:
            with contextlib.closing(urllib2.urlopen(request)) as response:
                if response.headers['Content-Type'] == 'application/json':
                    return json.load(response)
                else:
                    return response.read()
        except urllib2.HTTPError as e:
            if e.code == 403:
                raise NotAuthorized()
            elif e.code == 404:
                raise NotFound()
            else:
                raise
