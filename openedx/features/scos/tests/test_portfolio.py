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
from openedx.features.scos.conf import TESTING, DEBUG_OUTPUT_FILE \
	,ENV ,set_environment

conf.TESTING = True
set_environment('PREPROD')

import openedx.features.scos.enrolls as e
from openedx.features.scos.enrolls import *

import openedx.features.scos.users as u
from openedx.features.scos.users import *

import openedx.features.scos.courses as c
from openedx.features.scos.courses import *

import openedx.features.scos.portfolio as p
from openedx.features.scos.portfolio import *


#import pdb;pdb.set_trace()


test_course = 'interfinance+2018'
test_course = get_course_id_by_pattern(test_course)
test_user = '98finuni'

scos_cid = get_course_scos_id(test_course)
assert scos_cid
scos_uid = get_user_scos_id(test_user)
assert scos_uid

enroll_scos_user(test_course, test_user)
assert enrollment_exists(scos_cid, scos_uid)

with open(DEBUG_OUTPUT_FILE) as f:
	s = f.read()
	print s
	assert 'enrollDate' in s


unenroll_scos_user(test_course, test_user)
assert not enrollment_exists(scos_cid, scos_uid)

with open(DEBUG_OUTPUT_FILE) as f:
	s = f.read()
	print s
	assert 'usiaId' in s
	assert 'enrollDate' not in s


resp = check_scos_enrollment(test_course, test_user)
print resp
assert 'statusType' in resp and 'data' in resp


print '\nSUCCESS'
