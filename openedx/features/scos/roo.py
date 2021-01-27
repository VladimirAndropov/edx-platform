# -*- coding: utf-8 -*-
"""ROO interaction module"""

import sys
import os
import inspect
import io
import requests
import json
import csv
import exceptions

from openedx.features.scos.conf import ENV, HTTP_TIMEOUT, TESTING, DEBUG_OUTPUT_FILE, SSL_KEY, SSL_CERT
from openedx.features.scos.lib import ServerSession, ImpatientHTTPAdapter \
    ,JSON_HEADER, write_json, logit
from openedx.features.scos.courses import add_scos_course_to_list, get_course_scos_data \
    ,upate_course_scos_data, get_course_scos_id
from openedx.features.scos.users import get_user_scos_id
from openedx.features.scos.enrolls import enrollment_exists


api = None

# def get_api_requester():
# 	"""Create session for SCOS API interaction"""
# 	session = ServerSession(ENV('API_URL'))
# 	session.auth = (ENV('API_USER'), ENV('API_PASSWORD'))
# 	session.mount('http://', ImpatientHTTPAdapter(HTTP_TIMEOUT))
# 	session.mount('https://', ImpatientHTTPAdapter(HTTP_TIMEOUT))
# 	return session

data = {}

def get_api_requester():
    session = requests.Session()
    url = ENV('API_URL')  + 'v1/connection/check'
    session.get(url,  headers=JSON_HEADER, cert=(SSL_CERT, SSL_KEY))
    # session.mount('http://', ImpatientHTTPAdapter(HTTP_TIMEOUT))
    # session.mount('https://', ImpatientHTTPAdapter(HTTP_TIMEOUT))
    return session

def register_course(cid):
    if get_course_scos_id(cid):
        errorMsg = 'Course ' + cid + ' is already registered.'
    if 'preprod' in ENV('COURSES_DIR'):
        errorMsg += '\nFor PREPROD env do:\n' \
            + 'remove_scos_course_from_list(course_id)\n' \
                + 'upate_course_scos_data(course_id, {"id":""})'
    exceptions.RuntimeError(errorMsg)
    title = get_course_scos_data(cid)['title']
    scos_id = post_course_data(cid)
    if not scos_id:
        exceptions.RuntimeError('Unexpected error occured during the registration of ' + cid + ' course')
    add_scos_course_to_list(cid, title, scos_id)
    upate_course_scos_data(cid, {'id':scos_id})
    return scos_id

def post_course_data(cid):
    # """Send course metadata to ROO"""
    global api
    caller = inspect.stack()[1][3]
    is_new_course = 'register_course' in caller
    data = get_course_scos_data(cid, returnFullPackage = True)
    if data['partnerId'] != ENV('PLATFORM_ID'):
        raise exceptions.RuntimeError('partnerId mismatch between '
                                      + 'current env and SCOS metadata for course ' + cid)
    if is_new_course:
        del data['package']['items'][0]['id']
    # if TESTING:
    #     write_json(data)
    #     return 'DUMMY_COURSE_ID'
    if api is None:
        api = get_api_requester()
    # url = 'courses/v0/course' 
    url = ENV('API_URL')  + 'courses/v0/course' 
    if is_new_course:
        resp = api.post(url, json=data, headers = JSON_HEADER)
    else:
        resp = api.put(url, json=data, headers = JSON_HEADER)
    print 'Course data uploaded to SCOS. Status:', resp.status_code
    if resp.text:
        print 'Response:', resp.text
    resp.raise_for_status()
    if is_new_course:
        resp_data = resp.json()
        return resp_data['course_id']


def post_new_course_data(cid,data):
    # """Send course metadata to ROO"""
    global api
    # data = get_course_scos_data(cid, returnFullPackage = True)
    # del data['package']['items'][0]['id']
    if api is None:
        api = get_api_requester()
        
    url = ENV('API_URL')  + 'courses/v0/course' 
    resp = api.post(url, json=data, headers = JSON_HEADER)

    print 'Course data uploaded to SCOS. Status:', resp.status_code
    resp_data = resp.json()
    return resp_data['course_id']
    
    
def get_course_moderation_status(cid):
    # """Get course moderation status from ROO"""
    global api
    data = get_course_scos_data(cid)
    scos_id = data['id']
    if api is None:
        api = get_api_requester()
    url = ENV('API_URL')  + 'courses/v0/get_moderation_status?course_id='
    resp = api.get(url + scos_id)
    # resp = api.get(url + scos_id, data=json.dumps(payload),  headers=headers, cert=(SSL_CERT, SSL_KEY))
    print resp.text
    resp.raise_for_status()
    resp_data = resp.json()
    if not resp_data['status']:
        raise exceptions.RuntimeError('Unexpected error occured'
                                      + ' when trying to get moderation status')
    print 'SCOS course moderation status:', resp_data['status']
    return resp_data['status']


def change_course_status(cid, status):
    # """Change course status (active/archive) at ROO"""
    global api
    if status not in ('active', 'archive'):
        raise exceptions.RuntimeError('Unrecognized status: ' + status)
    data = get_course_scos_data(cid)
    scos_id = data['id']
    if api is None:
        api = get_api_requester()
    url = ENV('API_URL')  + 'courses/v0/update_status?course_id=' + scos_id + '&new_status=' + status
    resp = api.put(url)
    print resp.text
    resp.raise_for_status()
    resp_data = resp.json()
    if not resp_data['status']:
        sys.exit('Unexpected error occured when trying to get '
                 + 'SCOS course state for course ' + cid)
    print 'New SCOS course state:', resp_data['status']
    return resp_data['status']


# def get_feedback_widget_context(request, cid):
#     """Get data for SCOS feedback widget from ROO"""
#     global api
#     uid = request.user.username
#     scos_uid = get_user_scos_id(uid)
#     scos_cid = get_course_scos_id(cid)
#     url = '1.0/rest/exp/courses?cid=' + scos_cid
#     if api is None: api = get_api_requester()
#     resp = api.get(url)
#     resp_json = resp.json()
#     course_item_url = ''
#     visitors_rating = None
#     if 'item' in resp_json:
# 	course_item_url = resp_json['item']['course_item_url']
# 	#https://online.edu.ru/courses/item/?id=977&vid=1303#feedback
# 	visitors_rating = resp_json['item']['visitors_rating']
#     if course_item_url and ENV('DOMAIN') not in course_item_url:
# 	from urlparse import urlparse
# 	url = urlparse(course_item_url)
# 	url.netloc = ENV('DOMAIN')
# 	course_item_url = url.geturl()
#     cabinet_course_url = ''
#     if scos_uid and scos_cid and enrollment_exists(scos_cid, scos_uid):
# 	cabinet_course_url = 'https://' + ENV('DOMAIN') \
# 	    + '/ru/_profiles/leave-course-feedback' \
# 	    + '?cid=' + scos_cid + '&uid=' + scos_uid
#     context = {
# 	'course_item_url': course_item_url,
# 	'cabinet_course_url': cabinet_course_url,
# 	'user_id': uid,
# 	'visitors_rating': visitors_rating
#     }
#     logit('Feedback widget requested.'
# 	+ '  cid: ' + cid + '  uid: ' + uid
# 	+ '  course_item_url: ' + course_item_url
# 	+ '  cabinet_course_url: ' + cabinet_course_url
# 	+ '  current_rating: ' + str(visitors_rating))
#     return context

def get_widget_data(course_id):
    global api
    data = get_course_scos_data(course_id, True)
    version = data['package']['items'][0]['business_version']    
    url = 'https://'+ENV('DOMAIN')+'/public/widgets/feedback-widget?courseid={}&version={}'.format(get_course_scos_id(course_id),version)
    if api is None: 
        api = get_api_requester()
    resp = api.get(url,  headers=JSON_HEADER, timeout=1)
    if resp.status_code == 200:
        resp_data=(resp.text.encode('utf8'))
    return resp_data

def get_widget_url(course_id):
    data = get_course_scos_data(course_id, True)
    version = data['package']['items'][0]['business_version']    
    url = 'https://'+ENV('DOMAIN')+'/public/widgets/feedback-widget?courseid={}&version={}'.format(get_course_scos_id(course_id),version)
    return url

def get_generic_id(course_id):
    generic_id = ""
    #filestore = '/edx/var/scos/courses/testplt/list.csv'
    filestore = ENV('COURSES_DIR') + '/' + SCOS_COURSES_FILE
    with open(filestore) as csv_file:
        readCSV = csv.reader(csv_file, delimiter=';')
        for row in readCSV:
            if row[0] == str(course_id):
                generic_id = row[2]
    return (generic_id)