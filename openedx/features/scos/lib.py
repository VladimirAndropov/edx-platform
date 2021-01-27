# -*- coding: utf-8 -*-
"""Auxillary classes and functions"""

import sys
import os
import inspect
import io
import logging
import requests
import json

from conf import ENV, DEBUG_OUTPUT_FILE, LOG_FILE, console


JSON_HEADER = {'Content-type': 'application/json'}


class ImpatientHTTPAdapter(requests.adapters.HTTPAdapter):
	# """Custom HTTP adapter with timeout option"""
    def __init__(self, timeout=None, *args, **kwargs):
        self.timeout = timeout
        super(ImpatientHTTPAdapter, self).__init__(*args, **kwargs)
    def send(self, *args, **kwargs):
        kwargs['timeout'] = self.timeout
        return super(ImpatientHTTPAdapter, self).send(*args, **kwargs)


class ServerSession(requests.Session):
	"""HTTP connection wrapper with pre-set settings"""
	def __init__(self, url_base=None, *args, **kwargs):
		super(ServerSession, self).__init__(*args, **kwargs)
		self.url_base = url_base
	def request(self, method, url, **kwargs):
		absolute_url = self.url_base + url
		return super(ServerSession, self).request(
					method, absolute_url, **kwargs)


def merge_dicts(x, y):
	"""Merges two dictionaries"""
	z = x.copy()
	z.update(y)
	return z


def write_json(data, filename = DEBUG_OUTPUT_FILE):
	"""Write custom JSON file to disk"""
	json_data = json.dumps(
		data
		,ensure_ascii = False
		,indent = 4
		,separators = (',', ': ')
	)
	with io.open(filename, mode = 'w+', encoding = 'utf8') as f:
		f.write(unicode(json_data))


def logit(msg, level = 'INFO ', dest = LOG_FILE):
	"""Log custom message to disk file"""
	msg = msg.replace('\n', '').replace('\r', '')
	caller = inspect.stack()[1][3]
	if level[0].upper() in ('ERROR'[0], 'CRITICAL'[0]):
		msg = caller + '(): ' + msg
	msg = '[' + ENV('NAME') + ']  ' + msg
	from time import localtime, strftime
	rec = strftime('%d-%b-%Y %H:%M:%S', localtime()) \
		+ '  ' + level.upper() + '  ' + msg + '\n'
	try:
		with io.open(dest, mode = 'a+', encoding = 'utf8') as f:
			f.write(unicode(rec))
	except:
		pass
	if console:
		print msg
