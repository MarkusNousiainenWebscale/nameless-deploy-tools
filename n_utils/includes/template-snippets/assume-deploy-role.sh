#!/bin/bash

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

set -e

CF_paramBakeRoleStack="bakery-roles"
CF_AWS__Region="eu-west-1"

ROLE_ARN=$(show-stack-params-and-outputs.sh ${CF_AWS__Region} ${CF_paramBakeRoleStack} | jq -r .deployRoleArn)
assume-role.sh $ROLE_ARN