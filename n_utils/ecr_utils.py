#!/usr/bin/env python

# Copyright 2016-2017 Nitor Creations Oy
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import base64

import boto3
from botocore.exceptions import ClientError

from .cf_utils import region

def ensure_repo(name):
    ecr = boto3.client("ecr", region_name=region())
    repo = None
    try:
        repo_resp = ecr.describe_repositories(repositoryNames=[name])
        if 'repositories' in repo_resp:
            repo = repo_resp['repositories'][0]
    except ClientError:
        repo_resp = ecr.create_repository(repositoryName=name)
        if 'repository' in repo_resp:
            repo = repo_resp['repository']
    if not repo:
        raise Exception("Failed to find or create repo")
    print "REPO=\"" + repo['repositoryUri'] + "\""
    token_resp = ecr.get_authorization_token(registryIds=[repo['registryId']])
    if 'authorizationData' in token_resp:
        auth_data = token_resp['authorizationData'][0]
        full_token = base64.b64decode(auth_data['authorizationToken']).split(":")
        user = full_token[0]
        token = full_token[1]
        print "sudo docker login -u " + user + " -p " + token + " " + \
              auth_data['proxyEndpoint']
