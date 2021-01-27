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

import openedx.features.scos.conf as conf
from openedx.features.scos.conf import SCOS_ENROLLMENTS_FILE \
	,KEEP_SCOS_ENROLLMENTS_IN_MEM

import openedx.features.scos.enrolls as e
from openedx.features.scos.enrolls import *

import openedx.features.scos.users as u
from openedx.features.scos.users import *

import openedx.features.scos.courses as c
from openedx.features.scos.courses import *

#import pdb;pdb.set_trace()

test_list = [
	('dummy_course1','dummy_user1','dummy_time1'),
	('dummy_course2','dummy_user2','dummy_time2'),
	('dummy_course1','dummy_user2','dummy_time3'),
	('dummy_course2','dummy_user1','dummy_time4')
]


for t in test_list:
	add_enrollment(t[0], t[1], t[2])

assert enrollment_exists('dummy_course1','dummy_user1')
assert enrollment_exists('dummy_course2','dummy_user1')
c = get_enrolled_users('dummy_course1')
assert 'dummy_user1' in c
assert 'dummy_user2' in c
c = get_enrolled_courses('dummy_user1')
assert 'dummy_course1' in c
assert 'dummy_course2' in c

with open(SCOS_ENROLLMENTS_FILE) as f:
	s = f.read()
	print s
	assert 'dummy_course2;dummy_user1;dummy_time4\n' in s


for t in test_list:
	remove_enrollment(t[0], t[1])

assert not enrollment_exists('dummy_course1','dummy_user1')
assert not enrollment_exists('dummy_course2','dummy_user1')
assert not get_enrolled_users('dummy_course1')
assert not get_enrolled_courses('dummy_user1')

with open(SCOS_ENROLLMENTS_FILE) as f:
	s = f.read()
	print s
	assert 'dummy_course2;dummy_user1;dummy_time4\n' not in s


print '\nSUCCESS'
