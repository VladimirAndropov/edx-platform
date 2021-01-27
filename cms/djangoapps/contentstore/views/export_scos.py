import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from opaque_keys.edx.keys import CourseKey

from edxmako.shortcuts import render_to_response
from student.auth import has_course_author_access



import sys
import os
import io
import json
import exceptions

import pdb

from openedx.features.scos.conf import ENV, set_environment

from openedx.features.scos.roo import get_course_moderation_status, post_course_data, change_course_status, register_course, post_new_course_data

from openedx.features.scos.courses import get_course_scos_id, add_scos_course_to_list, get_course_scos_data,upate_course_scos_data, save_scos_courses_to_file, create_course_from_default



import copy
import datetime
import json
import unittest

import ddt
import mock
from django.conf import settings
from django.test.utils import override_settings
from pytz import UTC
from milestones.tests.utils import MilestonesTestCaseMixin
from mock import Mock, patch

from contentstore.utils import reverse_course_url, reverse_usage_url
from milestones.models import MilestoneRelationshipType
from models.settings.course_grading import CourseGradingModel, GRADING_POLICY_CHANGED_EVENT_TYPE, hash_grading_policy
from models.settings.course_metadata import CourseMetadata
from models.settings.encoder import CourseSettingsEncoder
from openedx.core.djangoapps.models.course_details import CourseDetails
from student.roles import CourseInstructorRole, CourseStaffRole

from util import milestones_helpers
from xblock_django.models import XBlockStudioConfigurationFlag
from xmodule.fields import Date
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import modulestore
from xmodule.tabs import InvalidTabsException



log = logging.getLogger(__name__)


@ensure_csrf_cookie
@login_required
def export_scos(request, course_key_string):
    course_key = CourseKey.from_string(course_key_string)
#     course_key_string = 'course-v1:fa+digitalmarket+2019_leto'
#     course_key
# CourseLocator(u'fa', u'digitalmarket', u'2019_leto', None, None)
    status = 'None'
    msg = ""
    current_env = ENV('DOMAIN')  
    
    if not has_course_author_access(request.user, course_key):
        raise PermissionDenied()
      
    if get_course_scos_id(course_key_string) is None:
        status = 'is_new_course'               
    
    # if status = 'None' and get_course_scos_id(course_key_string):
    #     status = get_course_moderation_status(course_key_string)
              
    course_module = modulestore().get_course(course_key)
    title = course_module.display_name
                  
    
    failed = False
    details = CourseDetails.fetch(course_key)
    log.debug('export_scos course_module=%s', course_module)
    # status = get_course_moderation_status(course_key_string) 
    # ok, failed, in_progress.
    jsondetails = json.dumps(details, cls=CourseSettingsEncoder)
    #jsondetails = json.dumps(details, default=lambda o: '<not serializable>')
    jsondetails = json.loads(jsondetails)    

    if 'action' in request.GET:
        if request.GET['action'] == 'push':
            try:
                cert = "false"
                data = get_course_scos_data(course_key_string, True)
                if jsondetails['certificate_available_date']:
                    cert = "true"
                # if jsondetails['duration']:
                #     upate_course_scos_data(course_key_string, {'id': jsondetails['duration']}) 
                if jsondetails['effort']:
                    upate_course_scos_data(course_key_string, {'duration': {"code": "week", "value": int(jsondetails['effort'])//54}})     
                teachers_json = jsondetails['instructor_info']
                for entry in teachers_json['instructors']:
                    entry['display_name']= entry['name']
                    entry['description']= entry['title']
                    entry['image']= "https://online.fa.ru"+entry['image']

                upate_course_scos_data(course_key_string, {
                "started_at": jsondetails['start_date'],
                "enrollment_finished_at": jsondetails['enrollment_end'],
                "finished_at": jsondetails['end_date'],
                "image": "https://online.fa.ru"+str(jsondetails['course_image_asset_path']),
                "description": jsondetails['short_description'],
                "external_url": "https://online.fa.ru/courses/"+str(course_key_string)+"/about",
                "content": jsondetails['overview'],                             
                "business_version": str(int(data['package']['items'][0]['business_version'])+1) ,
                "promo_url": "https://youtu.be/"+str(jsondetails['intro_video']),
                "title": title,
                # 'id': jsondetails['effort'],
                "lectures": len(course_module.discussion_topics),
                "sessionid": course_key_string,
                "direction": jsondetails['learning_info'],
                "competences":jsondetails['description'],
                "results": jsondetails['subtitle'],
                "language": jsondetails['language'],
                "requirements": jsondetails['pre_requisite_courses'],
                "cert": cert,
                'teachers': jsondetails['instructor_info']['instructors']                    
                                             })
                post_course_data(course_key_string)

                msg = _('Course successfully exported to scos repository')
            except Exception as e:
                failed = True
                # upate_course_scos_data(course_key_string, {
                #     "business_version": str(int(data['package']['items'][0]['business_version'])-1)})
                msg = 'Failed  '+course_key_string + ' with error: '+str(e)
        elif request.GET['action'] == 'active':
            try:
                status = change_course_status(course_key_string, 'active')
                assert status == 'ACTIVE'
            except Exception as e:
                failed = True
                msg = 'Failed  '+status + ' with error: '+str(e) +' because status '+get_course_moderation_status(course_key_string) 
        elif request.GET['action'] == 'archive':
            try:
                status = change_course_status(course_key_string, 'archive')
                assert status == 'ARCHIVE'  
            except Exception as e:
                failed = True
                msg = 'Failed  '+status + ' with error: '+str(e) +' because status '+get_course_moderation_status(course_key_string)
        elif request.GET['action'] == 'new':
            try:
                create_course_from_default(course_key_string)
                cert = "false"
                if jsondetails['certificate_available_date']:
                    cert = "true"
                if jsondetails['effort']:
                    upate_course_scos_data(course_key_string, {'duration': {"code": "week", "value": int(jsondetails['effort'])//54}})     
                teachers_json = jsondetails['instructor_info']
                for entry in teachers_json['instructors']:
                    entry['display_name']= entry['name']
                    entry['description']= entry['title']
                    entry['image']= "https://online.fa.ru"+entry['image']

                upate_course_scos_data(course_key_string, {
                "started_at": jsondetails['start_date'],
                "enrollment_finished_at": jsondetails['enrollment_end'],
                "finished_at": jsondetails['end_date'],
                "image": "https://online.fa.ru"+str(jsondetails['course_image_asset_path']),
                "description": jsondetails['short_description'],
                "external_url": "https://online.fa.ru/courses/"+str(course_key_string)+"/about",
                "content": jsondetails['overview'],                             
                "promo_url": "https://youtu.be/"+str(jsondetails['intro_video']),
                "title": title,
                # 'id': jsondetails['duration'],
                "lectures": len(course_module.discussion_topics),
                "sessionid": course_key_string,
                "direction": jsondetails['learning_info'],
                "competences":jsondetails['description'],
                "results": jsondetails['subtitle'],
                "language": jsondetails['language'],
                "requirements": jsondetails['pre_requisite_courses'],
                "cert": cert,
                'teachers': jsondetails['instructor_info']['instructors']                    
                                             })
                data = get_course_scos_data(course_key_string, returnFullPackage = True)
                del data['package']['items'][0]['id']
                general_uid = post_new_course_data(course_key_string,data)
                add_scos_course_to_list(course_key_string, title, general_uid)
                upate_course_scos_data(course_key_string, {'id':general_uid})
                msg = _('New Course successfully created in course catalog /edx/var/scos/courses/')
                
            except Exception as e:
                failed = True
                msg = 'Failed  with error: '+str(e)
        elif request.GET['action'] == 'update':
            try:
                create_course_from_default(course_key_string)
                cert = "false"
                if jsondetails['certificate_available_date']:
                    cert = "true"
                if jsondetails['effort']:
                    upate_course_scos_data(course_key_string, {'duration': {"code": "week", "value": int(jsondetails['effort'])//54}})     
                teachers_json = jsondetails['instructor_info']
                for entry in teachers_json['instructors']:
                    entry['display_name']= entry['name']
                    entry['description']= entry['title']
                    entry['image']= "https://online.fa.ru"+entry['image']

                upate_course_scos_data(course_key_string, {
                "started_at": jsondetails['start_date'],
                "enrollment_finished_at": jsondetails['enrollment_end'],
                "finished_at": jsondetails['end_date'],
                "image": "https://online.fa.ru"+str(jsondetails['course_image_asset_path']),
                "description": jsondetails['short_description'],
                "external_url": "https://online.fa.ru/courses/"+str(course_key_string)+"/about",
                "content": jsondetails['overview'],                             
                "promo_url": "https://youtu.be/"+str(jsondetails['intro_video']),
                "title": title,
                'id': jsondetails['duration'],
                "lectures": len(course_module.discussion_topics),
                "sessionid": course_key_string,
                "direction": jsondetails['learning_info'],
                "competences":jsondetails['description'],
                "results": jsondetails['subtitle'],
                "language": jsondetails['language'],
                "requirements": jsondetails['pre_requisite_courses'],
                "cert": cert,
                'teachers': jsondetails['instructor_info']['instructors']                    
                                             })
                data = get_course_scos_data(course_key_string, returnFullPackage = True)
                # del data['package']['items'][0]['id']
                # general_uid = post_new_course_data(course_key_string,data)
                add_scos_course_to_list(course_key_string, title, jsondetails['duration'])
                # upate_course_scos_data(course_key_string, {'id':general_uid})
                msg = _('New Course successfully created in course catalog /edx/var/scos/courses/')
                
            except Exception as e:
                failed = True
                msg = 'Failed  with error: '+str(e)    
    return render_to_response('export_scos.html', {
        'context_course': course_module,
        'msg': msg,
        'failed': failed,
        'status': status,
        'current_env': current_env
    })