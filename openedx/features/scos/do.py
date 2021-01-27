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

"""
Call format: do.py {environment} {operation} {course_id} {user_id}
Example: /edx/bin/python.edxapp /edx/app/edxapp/edx-platform/openedx/features/scos/do.py preprod register interfinance
Example: /edx/bin/python.edxapp /edx/app/edxapp/edx-platform/openedx/features/scos/do.py testplt enrollment interfinance 98finuni

curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'grant_type=password&client_id=onlineacademy&client_secret=5a04d64a-246d-4468-8929-57f439aa6fa9&username=vvandropov@fa.ru&password=Ptvkzghjof22!' "https://auth.online.edu.ru/realms/portfolio/protocol/openid-connect/token"

curl -d access_token=eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJhRGlwanZQUFV0TDEwXy11M3Y3dlhvb0dKdzBYSDJ3bk9GZDJDWjNXVEJNIn0.eyJqdGkiOiIwYjkxMjgwMS1lYWU5LTQ0ZmYtOWM0Mi1kMWE1ZWRkYzIxMWUiLCJleHAiOjE2MDQxNzQ2NzMsIm5iZiI6MCwiaWF0IjoxNjA0MTc0MzczLCJpc3MiOiJodHRwczovL2F1dGgub25saW5lLmVkdS5ydS9yZWFsbXMvcG9ydGZvbGlvIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6ImZhZThmZmMwLWMwMzktNDUyNi1hNzE3LTk2ZjBmN2NlYTE3MiIsInR5cCI6IkJlYXJlciIsImF6cCI6Im9ubGluZWFjYWRlbXkiLCJhdXRoX3RpbWUiOjAsInNlc3Npb25fc3RhdGUiOiJhNmI5ZjRmZC04MDkxLTQzZDYtOTQ4YS0xMjkyOWQ4NDIzMzciLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHBzOi8vb25saW5lLmZhLnJ1Il0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJwcm9maWxlIGVtYWlsIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJWbGFkaW1pciBBbmRyb3BvdiIsInByZWZlcnJlZF91c2VybmFtZSI6InZ2YW5kcm9wb3ZAZmEucnUiLCJtaWRkbGVfbmFtZSI6IiIsImdpdmVuX25hbWUiOiJWbGFkaW1pciIsImZhbWlseV9uYW1lIjoiQW5kcm9wb3YiLCJlbWFpbCI6InZ2YW5kcm9wb3ZAZmEucnUifQ.M1-6ebD23IUuX8j-dbFzAeDokCMuWfKP2f20yl1mDU-h4gxO5BoMqfrCWtiuRxIeHdw5pDZTo-eYwxz4Uya1g_BTBYmWJvqo9sncJrZkNTgyluE2RJ2d3JIpGvjXlDjmvi2jFKMPiIeETPDmpX1f-daQcwiOaWGZT3WxBvnqeApx9aVUF9yZWMOhArBOID6YrmdGSgbrVRtc9Eu-U5wkNQqE1Dbm_uap00vPvP7XYsEx1bww9WnpNkQY_NGgz3oF_buAw3sOKlVA4lobPteUTN-X1FvJlXo3Yg9uR-mJzqeYbtOohzNeQ9_2q3dOCpb7gjC-LSaZ1cnajmFV6_uwDQ "https://auth.online.edu.ru/realms/portfolio/protocol/openid-connect/userinfo"

curl "https://auth.online.edu.ru/realms/portfolio/protocol/openid-connect/certs"

curl ENV('API_URL')+"courses/v0/get_moderation_status?course_id=15dab3e8-4ae1-491a-90b7-a3d5672ccaca"

curl -H -u vvandropov@fa.ru:Ptvkzghjof22! ENV('API_URL')+"courses/v0/get_moderation_status?course_id=15dab3e8-4ae1-491a-90b7-a3d5672ccaca"

python /edx/app/edxapp/edx-platform/openedx/features/scos/do.py testplt status interfinance onlineacademy
"""

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
