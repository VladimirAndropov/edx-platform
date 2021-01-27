# -*- coding: utf-8 -*-
"""Package management module"""

import sys
import os

import conf
from conf import set_environment, ENV, ENVS, console

conf.console = True

import courses
from courses import *
import users
from users import *
import roo
from roo import *
import portfolio
from portfolio import *


COURSE_OPERATIONS = (
	'register',
	'status',
	'activate',
	'deactivate',
	'update',
	#'reports',
)
USER_OPERATIONS = (
	'enroll',
	'unenroll',
	'enrollment',
	#'result',
	#'cert',
)


if len(sys.argv) < 4:
	sys.exit('Required arguments not provided.')


env_name = sys.argv[1].upper()
operation = sys.argv[2]
coursename = sys.argv[3]
username = sys.argv[4] if len(sys.argv) > 4 else None


if env_name not in ENVS:
	sys.exit('Environment "' + env_name + '" is not supported.')

set_environment(env_name)

cid = get_course_id_by_pattern(coursename)

if operation in COURSE_OPERATIONS:
	pass
elif operation in USER_OPERATIONS:
	if not username:
		sys.exit('Username was not provided.')
	if '@' in username:
		sys.exit('Username must not contain "@" sign.')
else:
	sys.exit('Operation "' + operation + '" is not supported.')


if operation == 'register':
	register_course(cid)
elif operation == 'status':
	get_course_moderation_status(cid)
elif operation == 'activate':
	change_course_status(cid, 'active')
elif operation == 'deactivate':
	change_course_status(cid, 'archive')
elif operation == 'update':
	post_course_data(cid)
elif operation == 'reports':
	pass
elif operation == 'enroll':
	enroll_scos_user(cid, username)
elif operation == 'unenroll':
	unenroll_scos_user(cid, username)
elif operation == 'enrollment':
	check_scos_enrollment(cid, username)
elif operation == 'result':
	pass
elif operation == 'cert':
	pass
