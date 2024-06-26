#
# Copyright (c) 2024. All rights reserved.
#
# This software and all trademarks, trade names, and logos included herein are the property of Catalink and its affiliates, subsidiaries and licensors.
#

import sys
import urllib
import com.xhaus.jyson.JysonCodec as json
from xlrelease.HttpRequest import HttpRequest

SUCCESS_STATUS_CODE = 200
RECORD_CREATED_STATUS = 201
SERVICE_NOW_CREATE_URL = "/x_xlbv_xl_release_api_queue.do?JSONv2&sysparm_action=insert"


class CTLServiceNowClient(object):
    def __init__(self, httpConnection, username=None, password=None):
        self.headers = {'Content-type': 'application/json; charset=UTF-8'}
        self.accessToken = None
        self.refreshToken = None
        self.httpConnection = httpConnection
        self.useServicenowApp = httpConnection['useServicenowApp']
        self.useOAuth = httpConnection['useOAuth']
        self.service_now_url = httpConnection['url'].rstrip("/")
        if username:
            self.httpConnection['username'] = username
        if password:
            self.httpConnection['password'] = password
        self.httpRequest = HttpRequest(self.httpConnection, username, password)
        self.sysparms = 'sysparm_display_value=%s&sysparm_input_display_value=%s' % (self.httpConnection['sysparmDisplayValue'], self.httpConnection['sysparmInputDisplayValue'])
        self.apiEndpoint = '/api/now/table'

        if httpConnection['customApiEndpoint']:
            customApiEndpoint = httpConnection['customApiEndpoint'].strip('/')
            self.apiEndpoint = '/' + customApiEndpoint

    @staticmethod
    def create_client(httpConnection, username=None, password=None):
        return CTLServiceNowClient(httpConnection, username, password)

    def issue_token(self):
        tokenData = self.create_token(self.httpConnection)
        self.accessToken = tokenData['access_token']
        self.refreshToken = tokenData['refresh_token']
        self.headers['Authorization'] = "Bearer %s" % (self.accessToken)

    def create_token(self, httpConnection):
        servicenow_oauth_url = "/oauth_token.do"
        oauthConnection = {
            'url': httpConnection['url'],
            'oauthUsername': httpConnection['oauthUsername'],
            'oauthPassword': httpConnection['oauthPassword'],
            'clientId': httpConnection['clientId'],
            'clientSecret': httpConnection['clientSecret'],
            'proxyHost': httpConnection['proxyHost'],
            'proxyPort': httpConnection['proxyPort'],
            'proxyUsername': httpConnection['proxyUsername'],
            'proxyPassword': httpConnection['proxyPassword'],
            'proxyDomain': httpConnection['proxyDomain']
        }
        if httpConnection['oauthServer']:
            oauthConnection['url'] = httpConnection['oauthServer']
            if httpConnection['oauthServerEndpoint']:
                servicenow_oauth_url = httpConnection['oauthServerEndpoint'].strip('/')
                servicenow_oauth_url = '/' + servicenow_oauth_url
            else:
                servicenow_oauth_url = "/"
            if not httpConnection['oauthUsername'] and not httpConnection['oauthPassword']:
                oauthConnection['oauthUsername'] = httpConnection['username']
                oauthConnection['oauthPassword'] = httpConnection['password']
        content = {'grant_type': 'password', 'client_id': oauthConnection['clientId'],
                   'client_secret': oauthConnection['clientSecret'],
                   'username': oauthConnection['oauthUsername'], 'password': oauthConnection['oauthPassword']}
        httpRequest = HttpRequest(oauthConnection, None, None)
        if httpConnection['oauthAuthHeader']:
            response = httpRequest.post(servicenow_oauth_url, body=urllib.urlencode(content),
                                    contentType='application/x-www-form-urlencoded',  headers={'Authorization': httpConnection['oauthAuthHeader']})
        else:
            response = httpRequest.post(servicenow_oauth_url, body=urllib.urlencode(content),
                                        contentType='application/x-www-form-urlencoded')
        if response.getStatus() == SUCCESS_STATUS_CODE:
            data = json.loads(response.getResponse())
            return data
        print 'Could not get access token'
        self.throw_error(response)

    def revoke_token(self):
        if self.httpConnection['oauthServer']:
            self.accessToken = None
            self.refreshToken = None
        else:
            httpRequest = HttpRequest(self.httpConnection, None, None)
            servicenowApiUrl = "/oauth_revoke_token.do?token=%s" % self.accessToken
            response = httpRequest.get(servicenowApiUrl)
            servicenowApiUrl = "/oauth_revoke_token.do?token=%s" % self.refreshToken
            response = httpRequest.get(servicenowApiUrl)

    def print_table(self, headers, rows):
        print "\n|", "|".join(headers), "|"
        print "|", " ------ |" * len(headers)
        for r in rows:
            print "| ", "  |".join(r), " |"
        print "\n"

    def print_error(self, response):
        if type(response) is dict:
            outStr =   "| Status  | %s |\n" % ( response["status"] )
            outStr = "%s| Message | %s |\n" % ( outStr, response["error"]["message"] )
            outStr = "%s| Detail  | %s |\n" % ( outStr, response["error"]["detail"] )
            return outStr
        return response

    def create_payload_header(self, table_name, action, identifier, xlr_task_id):
        return {"table": table_name, "action": action, "identifier": identifier, "xlrTaskId": xlr_task_id}

    def create_payload(self, header, data):
        return json.dumps({"payload": json.dumps({'header': header, 'data': data})})

    def create_record(self, table_name, content, xlr_task_id):
        if self.useServicenowApp:
            payload_header = self.create_payload_header(table_name=table_name, action="create", identifier="", xlr_task_id=xlr_task_id)
            payload = self.create_payload(header=payload_header, data=content)
            data = self.request(method='POST', url=SERVICE_NOW_CREATE_URL, body=payload.encode('utf-8'), headers=self.headers)[0]
            if data["sys_row_error"] != "":
                raise RuntimeError(data["sys_row_error"])
            return data
        else:
            servicenow_api_url = self.apiEndpoint+'/%s?%s' % (table_name, self.sysparms)
            body = json.dumps(content)
            data = self.request(method='POST', url=servicenow_api_url, body=body.encode('utf-8'), headers=self.headers)
            if 'sys_id' in data:
                data['target_sys_id'] = data['sys_id']
            if 'number' in data:
                data['target_record_number'] = data['number']
            return data

    def get_record_with_fields(self, table_name, sys_id, fields):
        servicenow_api_url = self.apiEndpoint+'/%s?number=%s&sysparm_fields=%s&%s' % (table_name, sys_id, ",".join(fields), self.sysparms)
        response = self.httpRequest.get(servicenow_api_url, contentType='application/json', headers=self.headers)
        if self.useOAuth :self.revoke_token()

        if response.getStatus() == SUCCESS_STATUS_CODE:
            data = json.loads(response.getResponse())
            if len(data['result']) == 1:
                return data['result'][0]
        self.throw_error(response)

    def find_record(self, table_name, query):
        servicenow_api_url = self.apiEndpoint+'/%s?sysparm_query=%s&%s' % (table_name, query, self.sysparms)
        return self.request(method='GET', url=servicenow_api_url, headers=self.headers)

    def query(self, table_name, query, fail_on_not_found=False):
        result = self.find_record(table_name, query)
        size = len(result)
        if size == 1:
            return result[0]
        elif size > 1:
            raise Exception("Expected to find only 1 entry with query '%s' but found %s" % (query, size))
        if fail_on_not_found:
            raise Exception("No results found for query '%s'." % query)
        return None
    
    def queryOnetoMany(self, table_name, query, fail_on_not_found=False):
        result = self.find_record(table_name, query)
        return result

    def get_record(self, table_name, sys_id, fail_on_not_found=False):
        query = "sys_id=%s" % sys_id
        return self.query(table_name, query, fail_on_not_found)

    def find_by_name(self, name, table_name, fail_on_not_found=False):
        query = "name=%s" % name
        return self.query(table_name, query, fail_on_not_found)

    def create_link(self, table_name, sys_id):
        return "%s/nav_to.do?uri=%s.do?sys_id=%s" % (self.service_now_url, table_name, sys_id)

    def update_record(self, table_name, sys_id, content, xlr_task_id):
        if self.useServicenowApp:
            payload_header = self.create_payload_header(table_name=table_name, action="update", identifier=sys_id, xlr_task_id=xlr_task_id)
            payload = self.create_payload(header=payload_header, data=content)
            data = self.request(method='POST', url=SERVICE_NOW_CREATE_URL, body=payload.encode('utf-8'), headers=self.headers)[0]
            if data["sys_row_error"] != "":
                raise RuntimeError(data["sys_row_error"])
            return data
        else:
            servicenow_api_url = self.apiEndpoint+'/%s/%s?%s' % (table_name, sys_id, self.sysparms)
            body = json.dumps(content)
            data = self.request(method='PUT', url=servicenow_api_url, body=body.encode('utf-8'), headers=self.headers)
            if 'sys_id' in data:
                data['target_sys_id'] = data['sys_id']
            if 'number' in data:
                data['target_record_number'] = data['number']
            return data

    def check_connection(self):
        """
        Currently, there is no direct way to check if connection is successful or not for ServiceNow.
        As a solution, we are fetching single record from change_request table.
        :return: First record from change_request table if connection is successful, else throw error.
        """
        servicenow_api_url = self.apiEndpoint+'/{}?{}&sysparm_limit={}'.format('change_request', self.sysparms, 1)
        return self.request(method='GET', url=servicenow_api_url, headers=self.headers)

    def request(self, method, url, headers, content_type='application/json', body=None):
        if self.useOAuth:
            self.issue_token()

        if method == 'GET':
            response = self.httpRequest.get(url, contentType=content_type, headers=headers)
        elif method == 'PUT':
            response = self.httpRequest.put(url, body=body, contentType=content_type, headers=headers)
        else:
            response = self.httpRequest.post(url, body=body, contentType=content_type, headers=headers)

        if self.useOAuth:
            self.revoke_token()

        if response.getStatus() == SUCCESS_STATUS_CODE or response.getStatus() == RECORD_CREATED_STATUS:
            try:
                data = json.loads(response.getResponse())
                return data['result'] if 'result' in data else data['records']
            except:
                print response.getResponse()
                raise RuntimeError("Cannot convert to json")
        else:
            print response.getResponse()
            self.throw_error(response)

    def throw_error(self, response):
        print "Error from ServiceNow, HTTP Return: %s\n" % (response.getStatus())
        print "Detailed error: %s\n" % response.response
        if self.useOAuth:
            self.revoke_token()
        sys.exit(1)

    def EmptyToNone(self, value):
        if value is None or value.strip() == '':
            return None
        else:
            return value
