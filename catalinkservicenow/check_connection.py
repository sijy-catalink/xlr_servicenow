#
# Copyright (c) 2024. All rights reserved.
#
# This software and all trademarks, trade names, and logos included herein are the property of Catalink and its affiliates, subsidiaries and licensors.
#

from catalinkservicenow.client.CTLServiceNowClient import CTLServiceNowClient

params = {
    'url': configuration.url,
    'username': configuration.username,
    'password': configuration.password,
    'useServicenowApp': configuration.useServicenowApp,
    'useOAuth': configuration.useOAuth,
    'oauthServer': configuration.oauthServer,
    'oauthServerEndpoint': configuration.oauthServerEndpoint,
    'oauthUsername': configuration.oauthUsername,
    'oauthPassword': configuration.oauthPassword,
    'clientId': configuration.clientId,
    'clientSecret': configuration.clientSecret,
    'oauthAuthHeader':configuration.oauthAuthHeader,
    'proxyHost': configuration.proxyHost,
    'proxyPort': configuration.proxyPort,
    'proxyUsername': configuration.proxyUsername,
    'proxyPassword': configuration.proxyPassword,
    'proxyDomain': configuration.proxyDomain,
    'sysparmDisplayValue': configuration.sysparmDisplayValue,
    'sysparmInputDisplayValue': configuration.sysparmInputDisplayValue,
    'customApiEndpoint':configuration.customApiEndpoint
}

sn_client = CTLServiceNowClient.create_client(params)
content = sn_client.check_connection()
