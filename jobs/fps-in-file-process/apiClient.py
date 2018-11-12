import sys
import getopt
import os
import shutil
import logging
import requests
import json
sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir+'/modules/models'))
import transaction

class ApiClient:
    def __init__(self, config):
        self.config = config

    def get_token(self):
        url = self.config['api_login_url'] + '/login'
        user = self.config['api_user']
        password = self.config['api_password']
        headers = {'content-type': 'application/json'}
        body = '{"usr": "%s", "pwd": "%s"}' % (user, password)
        response = requests.post(url, headers=headers, data=body, verify=False)
        return response

    def send_payment(self, token, json):
        url = self.config['api_url'] + '/fps/sendPayment'
        headers = {'content-type': 'application/json',
                   'authorization': 'Bearer {}'.format(token)}
        body = json
        response = requests.post(url, headers=headers, data=body, verify=False)
        return response


