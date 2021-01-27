# -*- coding: utf-8 -*-

"""
Preferably run this as a web server user
"""

import sys
import os
import io
import json
import exceptions

import pdb

import openedx.features.scos.users as conf
from openedx.features.scos.conf import SCOS_USERS_FILE \
	,KEEP_SCOS_USERS_IN_MEM

import openedx.features.scos.users as u
from openedx.features.scos.users import *

#import pdb;pdb.set_trace()


assert '.json' in SCOS_USERS_FILE

if not os.path.exists(SCOS_USERS_FILE):
	with io.open(SCOS_USERS_FILE, mode = 'w+', encoding='utf8') as f:
		f.write(u'{"_TestUser_":"dummy_scos_id"}')
	os.chmod(SCOS_USERS_FILE, 0664)


conf.KEEP_SCOS_USERS_IN_MEM = True

assert get_user_scos_id('_TestUser_') == 'dummy_scos_id'
assert u.scos_users['_TestUser_'] == 'dummy_scos_id'

remove_scos_user('_TestUser_')
assert get_user_scos_id('_TestUser_') is None
assert '_TestUser_' not in u.scos_users

add_scos_user('_TestUser_', 'dummy_scos_id')
assert get_user_scos_id('_TestUser_') == 'dummy_scos_id'
assert u.scos_users['_TestUser_'] == 'dummy_scos_id'



conf.KEEP_SCOS_USERS_IN_MEM = False
u.scos_users = None

assert get_user_scos_id('_TestUser_') == 'dummy_scos_id'
assert u.scos_users is None

remove_scos_user('_TestUser_')
assert get_user_scos_id('_TestUser_') is None
assert u.scos_users is None

add_scos_user('_TestUser_', 'dummy_scos_id')
assert get_user_scos_id('_TestUser_') == 'dummy_scos_id'
assert u.scos_users is None



with io.open(SCOS_USERS_FILE, 'r', encoding = 'utf8') as f:
	s = f.read()
	assert '_TestUser_' in s
	assert 'dummy_scos_id' in s
	print 'FILE CONTENTS:'
	print s

print '\nSUCCESS'
