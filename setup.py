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

from setuptools import setup, find_packages

setup(
    name='skynet',
    version='1',
    description='Skyring Node Eventing Agent',
    long_description="skynet is the node eventing agent for Skyring."\
    " Each storage node managed by Skyring will have this agent running on them."\
    " It is a daemon which listens to dbus signals, filters it, "\
    "processes it and pushes the filtered signals to Skyring using"\
    " saltstack's eventing framework. Currently this daemon has capability"\
    " to send basic storage related, few node process related and"\
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

    packages = ["skynetd"],
    package_dir={
        'skynetd': 'src/skynetd'
    },

    install_requires=['python-daemon'],

    entry_points={
        'console_scripts': [
            'skynetd=skynetd.skynetd:main',
        ],
    },
)
