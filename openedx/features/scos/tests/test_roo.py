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

from openedx.features.scos.conf import ENV, set_environment

import openedx.features.scos.roo as r
from openedx.features.scos.roo import *

import openedx.features.scos.courses as c
from openedx.features.scos.courses import *

#import pdb;pdb.set_trace()


test_course = 'budgetary+2018_s'
test_descr = 'Курс формирует знания об особенностях планирования и финансирования бюджетных инвестиций, методологических основах управления капитальными расходами бюджетов публично-правовых образований; позволяет сформировать навыки отбора инвестиционных проектов для финансирования или софинансирования за счет бюджетных средств, мониторинга и оценки эффективности инвестиционных расходов бюджета.'

set_environment('PREPROD')
assert 'preprod' in ENV('COURSES_DIR')

cid = get_course_id_by_pattern(test_course)

status = get_course_moderation_status(cid)
if status == 'in_progress' or status == 'ok':
	sys.exit("Can't test this course now, it's already registered")
else:
	remove_scos_course_from_list(cid)
	upate_course_scos_data(cid, {"id": ""})


scos_id = register_course(cid)
assert len(scos_id) > 5

upate_course_scos_data(cid, {"description": test_descr+'..'})
post_course_data(cid)
upate_course_scos_data(cid, {"description": test_descr})

status = get_course_moderation_status(cid)
assert status == 'in_progress' or status == 'ok'

status = change_course_status(cid, 'archive')
assert status == 'ARCHIVE'
status = change_course_status(cid, 'active')
assert status == 'ACTIVE'


print '\nSUCCESS'
