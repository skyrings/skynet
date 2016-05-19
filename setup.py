#
# Copyright 2015 Red Hat, Inc.
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

import re
from setuptools import setup, Command
import subprocess


def read_module_contents():
    with open('src/skynetd/__init__.py') as skynet_init:
        return skynet_init.read()

module_file = read_module_contents()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", module_file))


class BumpCommand(Command):
    """ Bump the __version__ number and commit all changes. """

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        version = metadata['version'].split('.')
        version[-1] = str(int(version[-1]) + 1)  # Bump the final part

        try:
            print('old version: %s  new version: %s' %
                  (metadata['version'], '.'.join(version)))
            raw_input('Press enter to confirm, or ctrl-c to exit >')
        except KeyboardInterrupt:
            raise SystemExit("\nNot proceeding")

        old = "__version__ = '%s'" % metadata['version']
        new = "__version__ = '%s'" % '.'.join(version)

        module_file = read_module_contents()
        with open('src/skynetd/__init__.py', 'w') as fileh:
            fileh.write(module_file.replace(old, new))

        # Commit everything with a standard commit message
        cmd = ['git', 'commit', '-a', '-s', '-m',
               'version %s' % '.'.join(version)]
        print(' '.join(cmd))
        subprocess.check_call(cmd)


class ReleaseCommand(Command):
    """ Tag and push a new release. """

    user_options = [('sign', 's', 'GPG-sign the Git tag and release files')]

    def initialize_options(self):
        self.sign = False

    def finalize_options(self):
        pass

    def run(self):
        # Create Git tag
        version = metadata['version']
        tag_name = 'v%s' % version
        cmd = ['git', 'tag', '-a', tag_name, '-m', 'version %s' % version]
        if self.sign:
            cmd.append('-s')
        print(' '.join(cmd))
        subprocess.check_call(cmd)

        # Push Git tag to origin remote
        cmd = ['git', 'push', 'origin', tag_name]
        print(' '.join(cmd))
        subprocess.check_call(cmd)

        # Push package to pypi
        # TODO: package is not yet on pypi.
        # cmd = ['python', 'setup.py', 'sdist', 'upload']
        # if self.sign:
        #     cmd.append('--sign')
        # print(' '.join(cmd))
        # subprocess.check_call(cmd)

        # Push master to the remote
        cmd = ['git', 'push', 'origin', 'master']
        print(' '.join(cmd))
        subprocess.check_call(cmd)


setup(
    name='skynet',
    version=metadata['version'],
    description='Skyring Node Eventing Agent',
    long_description="skynet is the node eventing agent for Skyring."
    " Each storage node managed by Skyring will have this agent running on"
    " them. It is a daemon which listens to dbus signals, filters it, "
    "processes it and pushes the filtered signals to Skyring using"
    " saltstack's eventing framework. Currently this daemon has capability"
    " to send basic storage related, few node process related and"
    " network related events.",

    # The project's main homepage.
    url='https://github.com/skyrings/skynet',

    # Author details
    author='Darshan N',
    author_email='darshan.n.2024@gmail.com',

    license='Apache License, Version 2.0',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Programming Language :: Python :: 2.7',
    ],

    keywords='Skyring node Eventing Agent',

    packages=["skynetd"],
    package_dir={
        'skynetd': 'src/skynetd'
    },

    entry_points={
        'console_scripts': [
            'skynetd=skynetd.skynetd:main',
        ],
    },
    cmdclass={'bump': BumpCommand, 'release': ReleaseCommand},
)
