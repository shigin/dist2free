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

from distutils.versionpredicate import VersionPredicate
import sys, os
import glob
import warnings

def read_name(path):
    makefile = os.path.join(path, 'Makefile')
    f = open(makefile, 'r')
    portname = ''
    suffix = ''
    prefix = ''
    for i in f.read().split('\n'):
        pair = i.split('=', 1)
        if len(pair) == 1:
            continue
        name, value = [x.strip() for x in pair]
        if name == 'PORTNAME':
            portname = value
        if name == 'PKGNAMESUFFIX':
            suffix = value
        if name == 'PKGNAMEPREFIX':
            prefix = value
    f.close()
    return prefix + portname + suffix

def get_package_path(name, default='misc'):
    if os.environ.has_key('PORTSDIR'):
        ports_dir = os.environ['PORTSDIR']
    else:
        ports_dir = '/usr/ports'
    result = glob.glob(os.path.join(ports_dir, '*', name))
    if len(result) > 1:
        warnings.warn("more then one category for '%s', first one is used" % \
            (name))
    elif len(result) == 0:
        if not name.startswith('py-'):
            return get_package_path('py-' + name, default)
        warnings.warn("can't find any directory for '%s', use '%s'" % \
            (name, default))
        return name, '/' + default + '/' + name
    path = result[0]
    assert path.startswith(ports_dir)
    return read_name(path), path[len(ports_dir):]

ver_bind = {'>': '>=', '>=': '>='}
use_bind = {'>': '+', '>=': '+'}
USE_LIST = {'apache': 'USE_APACHE'}

def get_use_deps(deps):
    preds = []
    for dep in deps:
        vp = VersionPredicate(dep)
        print vp.name
        if vp.name not in USE_LIST:
            continue
        if len(vp.pred) > 1:
            raise Exception("it's too complicated for me, sorry :(")
        if len(vp.pred) == 1:
            sign, version = vp.pred[0]
            if sign not in use_bind:
                # XXX it's bad, needs to see how to work with other sign
                raise Exception("i don't know how FreeBSD package works with it :(")
            add = str(version) + use_bind[sign]
        else:
            add = 'yes'
        preds.append('%s=%s' % (USE_LIST[vp.name], add))
    return "\n".join(preds)
    
def get_run_deps(deps):
    preds = []
    for dep in deps:
        vp = VersionPredicate(dep)
        if vp.name in USE_LIST:
            continue
        name, path = get_package_path(vp.name)
        if len(vp.pred) > 1:
            raise Exception("it's too complicated for me, sorry :(")
        if len(vp.pred) == 1:
            sign, version = vp.pred[0]
            if sign not in ver_bind:
                # XXX it's bad, needs to see how to work with other sign
                raise Exception("i don't know how FreeBSD package works with it :(")
            add = ver_bind[sign] + str(version)
        else:
            add = ''
        preds.append('%s%s:${PORTSDIR}%s' % (name, add, path))

    return " \\\n\t\t".join(preds)

