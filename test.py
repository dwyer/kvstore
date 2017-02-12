#!/usr/bin/env python
# -*-coding:utf-8-*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import api


client = api.ApiClient()

old_stats = client._fetch('/stores')

store = client.new_store()
client.store = store

try:
    client.get('hello')
    assert False
except api.NotFound as e:
    pass

client.set('hello', 'world')
assert client.get('hello') == 'world'
client.set('hello', 'place')
assert client.get('hello') == 'place'
token = client.new_token()
assert token

try:
    client.new_token()
    assert False
except api.NotAuthorized as e:
    pass

try:
    client.set('hello', 'error')
    assert False
except api.NotAuthorized as e:
    assert client.get('hello') == 'place'

try:
    client.set('error', 'error')
    assert False
except api.NotAuthorized as e:
    pass

try:
    client.get('error')
    assert False
except api.NotFound as e:
    pass

try:
    client.get_tokens()
    assert False
except api.NotAuthorized as e:
    pass

client.token = token

assert len(client.get_tokens()) == 1
token = client.new_token()
assert len(client.get_tokens()) == 2

client.delete_token(client.token)

try:
    client.get_tokens()
    assert False
except api.NotAuthorized as e:
    pass

client.token = token
assert len(client.get_tokens()) == 1

client.delete_token(client.token)
client.token = None
assert len(client.get_tokens()) == 0

client.set('error', 'error')
assert client.get('error') == 'error'

client.delete('error')
try:
    client.get('error')
    assert False
except api.NotFound as e:
    pass

client.delete_store()
try:
    client.get_store()
    assert False
except api.NotFound as e:
    pass

new_stats = client._fetch('/stores')
assert old_stats == new_stats

print('%(values)d values in %(stores)d stores' % new_stats)
