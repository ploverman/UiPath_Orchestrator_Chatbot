import requests
# from dotenv import load_dotenv
import os
import json
import logging

# Set logger
logger_format = '[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s'
logging.basicConfig(level=logging.INFO, format=logger_format)
logger = logging.getLogger('UiPathAPI')
# create file handler which logs even debug messages
fh = logging.FileHandler('UiPathAPI.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(logger_format)
logger.addHandler(fh)


class UiPathAPI:

    def __init__(self):
        # load_dotenv()
        self.host = os.getenv('HOST')
        print(self.host)
        self.token = None
        self.headers = {
            'Content-Type': "application/json",
        }
        if not self.token: self.authenticate()

    def authenticate(self):
        logger.info('Calling authenticate method...')
        url = self.host + '/api/Account/Authenticate'
        payload = {
            'tenancyName': os.getenv('TENANCY_NAME'),
            'usernameOrEmailAddress': os.getenv('USERNAME_OR_EMAIL_ADDRESS'),
            'password': os.getenv('PASSWORD')
        }

        response = requests.request("POST", url, data=json.dumps(payload), headers=self.headers, verify=False).json()
        if response.get('success'):
            logger.info('User authenticated')
            self.token = response.get('result')
            self.headers['Authorization'] = 'Bearer {}'.format(self.token)

    def get_all_assets(self):
        logger.info('Calling get_all_assets method...')
        url = self.host + '/odata/Assets'
        response = requests.request("GET", url, headers=self.headers, verify=False).json()
        logger.info('Returning assets')
        return response.get('value')

    def get_all_robots(self):
        logger.info('Calling get_all_robots method...')
        url = self.host + '/odata/Sessions'
        payload = {
            '$select': 'State',
            '$expand': 'Robot'
        }
        response = requests.request("GET", url, params=payload, headers=self.headers, verify=False).json()
        logger.info('Returning robots')
        return response.get('value')

    def get_all_sessions(self):
        logger.info('Calling get_all_sessions method...')
        url = self.host + '/odata/Sessions'
        response = requests.request("GET", url, headers=self.headers, verify=False).json()
        logger.info('Returning sessions')
        return response.get('value')

    def get_all_jobs(self, start_time_from=None, start_time_to=None, end_time_from=None, end_time_to=None, status=None):
        logger.info('Calling get_all_jobs method...')
        url = self.host + '/odata/Jobs'
        filter_clauses = []
        if start_time_from: filter_clauses.append('StartTime gt {}'.format(start_time_from))
        if start_time_to: filter_clauses.append('StartTime lt {}'.format(start_time_to))
        if end_time_from: filter_clauses.append('EndTime gt {}'.format(end_time_from))
        if end_time_to: filter_clauses.append('EndTime lt {}'.format(end_time_to))
        if status: filter_clauses.append("State eq '{}'".format(status.title()))
        payload = {}
        if filter_clauses:
            filter_clause = ' and '.join(filter_clauses)
            payload['$filter'] = filter_clause
            logger.info('[get_all_jobs] Filter clause = {}'.format(filter_clause))
        response = requests.request("GET", url, params=payload, headers=self.headers, verify=False).json()
        logger.info('Returning jobs')
        return response.get('value')