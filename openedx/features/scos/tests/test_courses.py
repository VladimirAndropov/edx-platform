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

from openedx.features.scos.conf import ENV, COURSES_ID_PREFIX \
	,SCOS_COURSES_FILE, set_environment

set_environment('PREPROD')
assert 'preprod' in ENV('COURSES_DIR')

import openedx.features.scos.courses as c
from openedx.features.scos.courses import *

#import pdb;pdb.set_trace()


course_id = COURSES_ID_PREFIX + 'fa+interfinance+2018'
title = u'Международные экономические и финансовые организации'
scos_id = 'cad8dfe4a7b7478e9649b6bd9aa44495'
pattern = 'interfinance+2018'
#course-v1:fa+interfinance+2018;Международные экономические и финансовые организации;50c9e29710474a52968ff88f53edee98


assert '.csv' in SCOS_COURSES_FILE

old_scos_id = get_course_scos_id(course_id)
if old_scos_id:
	remove_scos_course_from_list(course_id)
	upate_course_scos_data(course_id, {'id':''})
	assert course_id not in c.scos_courses
	assert not get_course_scos_id(course_id)
	assert not get_course_scos_data(course_id)['id']


add_scos_course_to_list(course_id, title, scos_id)
assert c.scos_courses[course_id]['title'] == title
assert c.scos_courses[course_id]['scos_id'] == scos_id
assert get_course_scos_id(course_id) == scos_id
assert get_course_id_by_pattern(pattern) == course_id

update_scos_course_in_list(course_id, title +'0', scos_id +'0')
assert c.scos_courses[course_id]['title'] == title +'0'
assert c.scos_courses[course_id]['scos_id'] == scos_id +'0'
assert get_course_scos_id(course_id) == scos_id +'0'

upate_course_scos_data(course_id, {'id':scos_id})
assert get_course_scos_data(course_id)['id'] == scos_id
assert len(get_course_scos_data(course_id)['title']) > 0
upate_course_scos_data(course_id, {'id':''})
assert get_course_scos_data(course_id)['id'] == ''

remove_scos_course_from_list(course_id)
assert course_id not in c.scos_courses
assert not get_course_scos_id(course_id)
assert get_course_id_by_pattern(pattern) == course_id


if old_scos_id:
	add_scos_course_to_list(course_id, title, old_scos_id)
	upate_course_scos_data(course_id, {'id': old_scos_id})
	assert c.scos_courses[course_id]['title'] == title
	assert c.scos_courses[course_id]['scos_id'] == old_scos_id
	assert get_course_scos_id(course_id) == old_scos_id
	assert get_course_scos_data(course_id)['id'] == old_scos_id


print '\nSUCCESS'
