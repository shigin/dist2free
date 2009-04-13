#!/usr/bin/env python

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.    

from distutils.core import setup
import dist2free

setup(
    name="dist2free",
    version="0.0.1",
    packages=['dist2free'],
    author="Alexander Shigin",
    author_email='shigin@rambler-co.ru',
    description="Creates pkg-plist, Makefile for FreeBSD package.",
    long_description="""Module was developed to create FreeBSD
    package from setup.py distutils.""",
    url="http://github.com/shigin/dist2free/tree/master",
    license='Apache License 2.0',
    classifiers=['misc'],
    options={'build_pkg': {'python_min_version': 2.5,
                           'name_prefix': True,
                          }}
)

