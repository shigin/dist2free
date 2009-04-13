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
from distutils.versionpredicate import VersionPredicate
from distutils.file_util import copy_file
import sys, os
import re
import warnings
import packages

def ens_tuple(value):
    if isinstance(value, basestring):
        return (value, )
    elif value is None:
        return tuple()
    else:
        return value

class build_pkg(Command):
    description = "create an FreeBSD package"
    user_options = [
        ('bdist-dir=', None,
         "base directory for creating built distributions"),
        ('optimize=', 'O',
         "enable optimization"),
        ('build-base=', 'b',
         "base directory for build library"),
        ('shell-file=', None,
         "location of the base file"),
        ('name-suffix=', None, 
         "do use name suffix"),
        ('name-prefix=', None, 
         "do use name prefix"),
        ('pkg-install=', None,
         "specify pkg-install file"),
        ('pkg-deinstall=', None,
         "specify pkg-deinstall file"),
        ('python-min-version=', None,
         "specify minimum python version"),
        ('periodic-daily=', None,
         "scripts for periodic daily"),
        ('rc-scripts=', None,
         "rc scripts"),
        ('configs=', None,
         "file to place in ${PREFIX}/etc"),
        ('extra-modules=', None,
         "extra modules in form ('path/module', ${MAKEFILE_VAR}/path)"),
        ('brief-prefix=', None,
         "prefix for brief description of the package"),
    ]

    def get_deps(self):
        return packages.get_run_deps(self.distribution.get_requires())

    def get_uses(self):
        return packages.get_use_deps(self.distribution.get_requires())

    def get_suffix(self):
        if self.name_suffix:
            return '${PYTHON_PKGNAMESUFFIX}'
        else:
            return ''

    def get_prefix(self):
        if self.name_prefix:
            return '${PYTHON_PKGNAMEPREFIX}'
        else:
            return ''

    def get_brief(self):
        if self.brief_prefix:
            return ' '.join(self.brief_prefix, self.distribution.get_description())
        else:
            return self.distribution.get_description()

    def get_pre_install(self):
        script = []
        if self.pkg_install:
            script.append('PKG_PREFIX=${PREFIX} ${SH} ${PKGINSTALL} ${PKGNAME} PRE-INSTALL') 
        if len(script) > 0:
            return "\n\t".join(["pre-install:"] + script)
        else:
            return ''

    def get_post_install(self):
        script = []
        if self.periodic_daily:
            script.append('mkdir -p ${PREFIX}/periodic/daily')
        for xperiodic in self.periodic_daily:
            periodic = xperiodic.split('/')[-1]
            script.append('${INSTALL_SCRIPT} ${FILESDIR}/%s ${PREFIX}/periodic/daily' % periodic)
        for xconfig in self.configs:
            config = xconfig.split('/')[-1]
            script.append("${INSTALL_DATA} ${FILESDIR}/%s ${PREFIX}/etc" % config)
        if self.pkg_install:
            script.append('PKG_PREFIX=${PREFIX} ${SH} ${PKGINSTALL} ${PKGNAME} POST-INSTALL') 
        for from_, to_ in self.extra_modules:
            file_name = from_.split('/')[-1]
            script.append("${INSTALL_DATA} ${FILESDIR}/%s %s" % (file_name, to_))
        if len(script) > 0:
            return "\n\t".join(["post-install:"] + script)
        else:
            return ''

    def get_pre_deinstall(self):
        script = []
        if self.pkg_deinstall:
            script.append('PKG_PREFIX=${PREFIX} ${SH} ${PKGDEINSTALL} ${PKGNAME} PRE-DEINSTALL') 
        if len(script) > 0:
            return '\n' + "\n\t".join(["pre-deinstall:"] + script)
        else:
            return ''

    def get_post_deinstall(self):
        script = []
        if self.pkg_deinstall:
            script.append('PKG_PREFIX=${PREFIX} ${SH} ${PKGDEINSTALL} ${PKGNAME} POST-DEINSTALL') 
        if len(script) > 0:
            return "\n\t".join(["post-deinstall:"] + script)
        else:
            return ''

    def get_python_min(self):
        if self.python_min_version:
            return str(self.python_min_version) + '+'
        else:
            return 'yes'

    def get_install_args(self):
        if self.optimize:
            return "-c -O1 --prefix=${PREFIX}"
        else:
            return "-c --prefix=${PREFIX}"

    def get_rcs(self):
        scripts = []
        for script in self.rc_scripts:
            # scripts/rc1.sh => rc1
            scripts.append(script.split('/')[-1].split('.')[0])

        return " ".join(scripts)

    port_options = { 'Makefile': [
        ('PORTNAME',        lambda self: self.distribution.get_name(),       None),
        ('PORTVERSION',     lambda self: self.distribution.get_version(),    None),
        ('PKGNAMESUFFIX',   get_suffix, ''),
        ('PKGNAMEPREFIX',   get_prefix, ''),
        ('CATEGORIES',      lambda self: " ".join(self.distribution.get_classifiers()), 'misc'),
        ('MASTER_SITES',    lambda self: self.distribution.get_url(),        ''),
        ('MAINTAINER',      lambda self: self.distribution.get_maintainer(), ''),
        ('COMMENT',         get_brief, ''),
        ('RUN_DEPENDS',     get_deps, ''),
        ('',                get_uses, ''),
        ('USE_PYTHON',      get_python_min, ''),
        ('USE_PYDISTUTILS', lambda self: "yes", ''),
        ('USE_RC_SUBR',     get_rcs, ''),
        ('',                get_pre_install, ''),
        ('',                get_post_install, ''),
        ('',                get_pre_deinstall, ''),
        ('',                get_post_deinstall, ''),
        ('', lambda self: '', ''),
        ('', lambda self: ".include <bsd.port.pre.mk>", ''),
        ('', lambda self: "PYTHON_CMD = ${PYTHONBASE}/bin/${PYTHON_VERSION}", ''),
        ('PYDISTUTILS_INSTALLARGS', get_install_args, None),
        ('', lambda self: ".include <bsd.port.post.mk>", ''),
        ],

        'pkg-descr': [
        ('',                lambda self: self.distribution.get_long_description(), '')
        ]
    }

    def initialize_options (self):
        for option in [x[0][:-1] for x in self.user_options]:
            setattr(self, option.replace("-", "_"), None)

    def finalize_options (self):
        if self.python_min_version:
            assert re.match(r'[0-9][.][0-9]', str(self.python_min_version))
        if self.pkg_install:
            assert os.path.isfile(self.pkg_install)
        if self.pkg_deinstall:
            assert os.path.isfile(self.pkg_deinstall)
        self.periodic_daily = ens_tuple(self.periodic_daily)
        self.rc_scripts = ens_tuple(self.rc_scripts)
        self.configs = ens_tuple(self.configs)
        if not self.extra_modules:
            self.extra_modules = []

        if not self.bdist_dir:
            self.bdist_dir = os.path.join(os.getcwd(), "build", self.distribution.get_name())
        self.defbdist = os.path.join(os.getcwd(), "build", "pkg")
        if not self.build_base:
            self.build_base = self.bdist_dir
        if not self.shell_file:
            self.shell_file = os.path.join(self.bdist_dir, 'all.sh')
        if not os.path.isdir(self.bdist_dir):
            os.makedirs(self.bdist_dir)

    def make_file(self, filename, options):
        fd = open(filename, "w") 
        try:
            for value, func, default in options:
                result = func(self)
#                try:
#                    result = func(self)
#                except Exception, err:
#                    warnings.warn(str(err))
#                    if default is None:
#                        raise
#                    else:
#                        result = default
                if result == "":
                    continue
                if value == "":
                    fd.write("%s\n" % result)
                else:
                    fd.write("%s = %s\n" % (value, result))
        finally:
            fd.close()

    def make_files(self):
        for file in self.port_options:
            self.execute(self.make_file, 
                (os.path.join(self.bdist_dir, file), self.port_options[file]),
                "creating %s file" % file)

    def make_shell(self, filename):
        fd = open(filename, "w")
        if self.optimize:
            args = '-O1'
        else:
            args = ''
        try:
            fd.write("""#!/usr/bin/env bash
TMP=`mktemp -d /tmp/pkg.XXXX`
[ -z $TMP ] && exit 1
%(python)s setup.py install %(args)s --root $TMP --record $TMP/pkg-plist
sed 's#%(prefix)s/lib/python2.[0-9]/site-packages#%(site)s#; s#^%(prefix)s/##' < $TMP/pkg-plist | grep -v "egg-info$" > %(target)s/pkg-plist
rm -rf $TMP
""" % {'prefix': sys.prefix, 'target': self.bdist_dir, 'site': '%%PYTHON_SITELIBDIR%%', 'args': args, 'python': sys.executable})
        finally:
            fd.close()

    def run_shell(self, filename):
        os.system("/usr/bin/env bash %s" % filename)
        os.remove(filename)

    def make_plist(self):
        if True: # well, we need some info about... not self.have_run.get('build'):
            cmd_obj = self.get_command_obj('install')
            cmd_obj.ensure_finalized()
            cmd_obj.run()
            self.have_run['build'] = 1

    def add_dirrm(self, fname):
#        cmd_obj = self.get_command_obj('build_py')
#        cmd_obj.ensure_finalized()
#        cmd_obj.run()
#        self.have_run['build_py'] = 1
        if not self.distribution.packages:
            return
        self.run_command('build')
        f = open(fname, 'a')
        for package in sorted(self.distribution.packages, key=len, reverse=True):
            f.write("@dirrm %%PYTHON_SITELIBDIR%%/" + package + "\n")
        f.close()

    def link_dir(self, from_, to_):
        if not os.path.islink(to_):
            os.system('ln -s %s %s' % (from_, to_))

    def add_pkgs(self, bdist):
        if self.pkg_install:
            copy_file(self.pkg_install, os.path.join(bdist, 'pkg-install'))
        if self.pkg_deinstall:
            copy_file(self.pkg_deinstall, os.path.join(bdist, 'pkg-deinstall'))

    def add_files(self, bdist):
        files_dir = os.path.join(bdist, 'files')
        if not os.path.isdir(files_dir):
            os.mkdir(files_dir)
        for file in self.rc_scripts:
            # script/qqqq.sh => qqqq.in
            in_file = file.split('/')[-1].split('.')[0] + '.in'
            copy_file(file, os.path.join(files_dir, in_file))
        modules = (x[0] for x in self.extra_modules)
        for file in self.configs + self.periodic_daily + tuple(modules):
            in_file = file.split('/')[-1]
            copy_file(file, os.path.join(files_dir, in_file))

    def add_extra(self, fname):
        f = open(fname, 'a')
        try:
            for file in self.periodic_daily:
                f.write(os.path.join('etc', 'periodic', 'daily', file) + '\n')
            for file in self.configs:
                f.write(os.path.join('etc', file) + '\n')
            for from_, to_ in self.extra_modules:
	        path = to_.replace('${', '%%').replace('}', '%%')
		if path.endswith('/'):
		    path += from_.split('/')[-1]
                f.write(path + '\n')
        finally:
            f.close()

    def run(self):
        self.make_files()

        self.execute(self.make_shell, (self.shell_file, ),
            "creating %s batch file" % self.shell_file)
        self.execute(self.run_shell, (self.shell_file, ),
            "executing the shell script")
        self.execute(self.add_extra, (os.path.join(self.bdist_dir, 'pkg-plist'), ),
            "adding extra files to pkg-plist")
        self.execute(self.add_dirrm, (os.path.join(self.bdist_dir, 'pkg-plist'), ),
            "adding dirrm for each package")
        self.execute(self.add_pkgs, (self.bdist_dir, ),
            "adding post install/deinstall")
        self.execute(self.add_files, (self.bdist_dir, ),
            "adding rc/conf files")
        self.execute(self.link_dir, (self.bdist_dir, self.defbdist),
            "linking dir %s to 'pkg'" % self.bdist_dir)
        print """now you can copy files from %s and run make package""" % self.bdist_dir
        
