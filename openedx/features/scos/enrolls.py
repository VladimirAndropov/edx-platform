# -*- coding: utf-8 -*-
"""SCOS course entollments management module"""

import sys
import os
import io
import csv
import exceptions

from conf import SCOS_ENROLLMENTS_FILE, KEEP_SCOS_ENROLLMENTS_IN_MEM


scos_enrolls = None


def load_enrolls_from_file(filename = SCOS_ENROLLMENTS_FILE):
	"""Load all SCOS users' enrollments data from file"""
	global scos_enrolls
	scos_enrolls = []
	with open(filename) as f:
		reader = csv.DictReader(f, delimiter = ';')
		reader.fieldnames = 'scos_cid', 'scos_uid', 'time'
		for row in reader:
			scos_enrolls.append(
				(row['scos_cid'],row['scos_uid'],row['time']))


def save_enrolls_to_file(filename = SCOS_ENROLLMENTS_FILE):
	"""Save all SCOS users' enrollments data to file"""
	global scos_enrolls
	if scos_enrolls is None:
		raise exceptions.RuntimeError(
			'scos_enrolls were not loaded yet')
	with open(filename, mode = 'w+') as f:
		for (scos_cid,scos_uid,time) in scos_enrolls:
			f.write(scos_cid + ';' + scos_uid + ';' + time + '\n')


def add_enrollment(scos_cid, scos_uid, time):
	"""Save SCOS user's course enrollment data to file.
	Args:
		scos_cid (str): SCOS course identificator.
		scos_uid (str): SCOS user identificator.
		time (str): Timestamp.
	"""
	global scos_enrolls
	if scos_enrolls is None:
		load_enrolls_from_file()
	match = [i for i in scos_enrolls
		if i[0] == scos_cid and i[1] == scos_uid]
	if not match:
		scos_enrolls.append( (scos_cid,scos_uid,time) )
		save_enrolls_to_file()
	if not KEEP_SCOS_ENROLLMENTS_IN_MEM:
		scos_enrolls = None


def remove_enrollment(scos_cid, scos_uid):
	"""Remove SCOS user course enrollment data from file"""
	global scos_enrolls
	if scos_enrolls is None:
		load_enrolls_from_file()
	match = [i for i in scos_enrolls
		if i[0] == scos_cid and i[1] == scos_uid]
	if match:
		scos_enrolls = [i for i in scos_enrolls
			if i[0] != scos_cid and i[1] != scos_uid]
		save_enrolls_to_file()
	if not KEEP_SCOS_ENROLLMENTS_IN_MEM:
		scos_enrolls = None


def enrollment_exists(scos_cid, scos_uid):

    global scos_enrolls
    if scos_enrolls is None:
        load_enrolls_from_file()
    match = [i for i in scos_enrolls
        if i[0] == scos_cid and i[1] == scos_uid]
    if not KEEP_SCOS_ENROLLMENTS_IN_MEM:
        scos_enrolls = None
    return True if match else False


def get_enrolled_users(scos_cid):
	"""Get a list of users enrolled in course"""
	global scos_enrolls
	if scos_enrolls is None:
		load_enrolls_from_file()
	matches = [i[1] for i in scos_enrolls if i[0] == scos_cid]
	if not KEEP_SCOS_ENROLLMENTS_IN_MEM:
		scos_enrolls = None
	return matches


def get_enrolled_courses(scos_uid):
	"""Get a list of courses a user is enrolled in"""
	global scos_enrolls
	if scos_enrolls is None:
		load_enrolls_from_file()
	matches = [i[0] for i in scos_enrolls if i[1] == scos_uid]
	if not KEEP_SCOS_ENROLLMENTS_IN_MEM:
		scos_enrolls = None
	return matches
