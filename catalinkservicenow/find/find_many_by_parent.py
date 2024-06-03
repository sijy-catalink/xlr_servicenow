#
# Copyright (c) 2024. All rights reserved.
#
# This software and all trademarks, trade names, and logos included herein are the property of Catalink and its affiliates, subsidiaries and licensors.
#

import json
import catalinkservicenow 

if classReload:
    reload(catalinkservicenow)

from catalinkservicenow import get_deep_link_url, add_code_compliance_record
from catalinkservicenow.client.CTLServiceNowClient import CTLServiceNowClient
from catalinkservicenow.helper.helper import assert_not_null
from catalinkservicenow.markdown.markdown_logger import MarkdownLogger as mdl

assert_not_null(parent, "Parent is mandatory")

sn_client = CTLServiceNowClient.create_client(servicenowServer, username, password)

query = "change_request=%s" % (parent)

result = sn_client.queryOnetoMany(tableName, query, True)

mdl.println(result)
sysIds = {}
changeTasksRaw = {}
indexSysIds={}
i=0

for item in result:
    change_sysid = item["sys_id"]
    indexSysIds[i]=change_sysid
    change_short_description = item["short_description"]
    sysIds[change_sysid]=change_short_description
    changeTasksRaw[change_sysid]=item
    i=i+1

