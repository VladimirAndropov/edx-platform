import json
import requests
from openedx.features.scos.roo import *

SSL_CERT = "/edx/app/edxapp/edx-platform/openedx/features/scos/keys/3928301200ea45e899d2e3a78a6db466_1634209477.crt"
SSL_KEY = "/edx/app/edxapp/edx-platform/openedx/features/scos/keys/3928301200ea45e899d2e3a78a6db466_1634209477.key"

data = {}
JSON_HEADER = {'content-type': 'text/html;charset=utf-8','content-length':'2'}


def get_api_requester():
    url = ENV('API_URL')+"v1/connection/check"
    resp = requests.get(url, data=json.dumps(payload),  headers=JSON_HEADER, cert=(SSL_CERT, SSL_KEY))
    return (resp.text.encode('utf8'))

# def get_widget_data(generic_id):
#     url = "https://"+ENV('DOMAIN')+"/public/widgets/feedback-widget?version=1&courseid="+str(generic_id)
#     resp = requests.get(url, data=json.dumps(payload),  headers=headers, cert=(SSL_CERT, SSL_KEY),timeout=1)
#     if resp.status_code == 200:
#         resp_data=(resp.text.encode('utf8'))
#     return (resp_data)

def get_widget_data(generic_id):
    url = "https://"+ENV('DOMAIN')+"/public/widgets/feedback-widget?version=1&courseid="+str(generic_id)
    resp = api.get(url, data=json.dumps(data),  headers=headers, timeout=1)
    if resp.status_code == 200:
        resp_data=(resp.text.encode('utf8'))
    return (resp_data)

