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

from distutils.core import Command
import sys, os

class make_pkg(Command):
    description = "makes FreeBSD package"
    user_options = [
        ("none=", None,
         "this is fake option"),
                   ]
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run_make(self):
        os.system('%s setup.py sdist' % sys.executable)
        os.system('%s setup.py build_pkg' % sys.executable)
        dir = os.getcwd()
        os.chdir(os.path.join(os.getcwd(), 'build', self.distribution.get_name()))
        print "make in %s" % os.getcwd()
        os.system('make DISTDIR=%(dir)s/dist/ install package' % \
                {'dir': dir})
        os.chdir(dir)

    def run(self):
        self.execute(self.run_make, tuple(),
            "run sdist, build_pkg, make...")
