# -*- coding: utf-8 -*-
"""Package configuration module"""

import os

TESTING = False
VERBOSE = True

DATA_DIR = '/edx/var/scos'
LOG_FILE = DATA_DIR + '/log.txt'
DEBUG_OUTPUT_FILE = DATA_DIR + '/debug.json'

SCOS_USERS_FILE = DATA_DIR + '/users.json'
KEEP_SCOS_USERS_IN_MEM = True
SCOS_ENROLLMENTS_FILE = DATA_DIR + '/enrollments.csv'
KEEP_SCOS_ENROLLMENTS_IN_MEM = True

MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
SSL_CERT = MODULE_DIR + '/keys/take from scos.crt'
SSL_KEY = MODULE_DIR + '/keys/take from scos.key'

SCOS_COURSES_FILE = 'list.csv'
COURSES_ID_PREFIX = 'course-v1:'
WIDGET_TEMPLATE_FILE = 'widget_template.html'

HTTP_TIMEOUT = 5

RU_STR = {
'Course reviews': 'Reviews'
}

DEFAULT_ENV = 'PROD'

ENVS = {}
ENVS['PROD'] = {
	'NAME': 'PROD',
	'PLATFORM_ID': 'take from scos',
	'INSTITUTION_ID': 'take from scos',
	'DOMAIN': 'online.edu.ru',
	'API_URL': 'https://online.edu.ru/api/',
	'API_USER': 'take from scos',
	'API_USER_ID': 'take from scos',
	'API_PASSWORD': 'take from scos',
	'PORTFOLIO_API_URL': 'https://portfolio.edu.ru/api/',
	'COURSES_DIR': DATA_DIR + '/courses/prod'
}


current_env = ENVS[DEFAULT_ENV]

console = False


def set_environment(name):
	global current_env
	current_env = ENVS[name]


def ENV(var, env_name = None):
	if env_name is None:
		return current_env[var]
	else:
		return ENVS[env_name][var]
