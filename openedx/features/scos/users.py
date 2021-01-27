# -*- coding: utf-8 -*-
"""SCOS users management module"""

import sys
import os
import io
import json
import exceptions

from conf import DATA_DIR, SCOS_USERS_FILE, KEEP_SCOS_USERS_IN_MEM
from django.db import transaction, connection


scos_users = None


def load_scos_users_from_file(filename = SCOS_USERS_FILE):
	# """Load SCOS users list from file"""
    global scos_users
    with io.open(filename, encoding = 'utf8') as f:
        scos_users = json.load(f)


def save_scos_users_to_file(filename = SCOS_USERS_FILE):
	"""Save SCOS users list from file"""
	global scos_users
	if scos_users is None:
		raise exceptions.RuntimeError('scos_users were not loaded yet')
	json_data = json.dumps(
		scos_users
		,ensure_ascii = False
		,indent = 0
		,separators = (',', ':')
	)
	with io.open(filename, mode = 'w+', encoding = 'utf8') as f:
		f.write(unicode(json_data))


def add_scos_user(username, scos_id):
	"""Add user to SOCS users list"""
	global scos_users
	if scos_users is None:
		load_scos_users_from_file()
	if username not in scos_users:
		scos_users[username] = scos_id
		save_scos_users_to_file()
	if not KEEP_SCOS_USERS_IN_MEM:
		scos_users = None


def remove_scos_user(username):
	"""Remove user from SCOS users list"""
	global scos_users
	if scos_users is None:
		load_scos_users_from_file()
	if username in scos_users:
		del scos_users[username]
		save_scos_users_to_file()
	if not KEEP_SCOS_USERS_IN_MEM:
		scos_users = None


# def get_user_scos_id(username):
# 	# """Get SCOS identificator of a user"""
#     global scos_users
#     scos_id = None
#     if scos_users is None:
#         load_scos_users_from_file()
#     if username in scos_users:
#         scos_id = scos_users[username]
#     if not KEEP_SCOS_USERS_IN_MEM:
#         scos_users = None
#     return scos_id

def get_user_scos_id(user_id):
    cursor = connection.cursor()
    query = ("""SELECT uid FROM edxapp.social_auth_usersocialauth  where user_id = '%s' ORDER BY ID DESC LIMIT 1""" % (user_id))
    cursor.execute (query)
    results = cursor.fetchall()
    for row in results:
        scos_id = row[0]        
    return scos_id

def get_user_scos_ids(user_ids):
    # user_ids = ["930", "35"]
    scos_ids = []
    if bad_scos_ids() >= 1:
        return False
    cursor = connection.cursor()
    query = "SELECT uid FROM edxapp.social_auth_usersocialauth WHERE user_id IN ('%s') " % "','".join(user_ids)
    cursor.execute(query)        
    results = cursor.fetchall()
    for key in reversed(results):
        b = key[0]
        scos_ids.append(b)
    return scos_ids    


def bad_scos_ids():
    cursor = connection.cursor()
    query = "SELECT user_id, COUNT(user_id) FROM edxapp.social_auth_usersocialauth GROUP BY  user_id HAVING COUNT(user_id) > 1"
    cursor.execute(query)
    results = cursor.fetchall()
    return len(results)