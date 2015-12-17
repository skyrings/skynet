#!/usr/bin/env python
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

import os
import errno
import logging
from constants import DEFAULT_LOG_FILE, DEFAULT_LOG_LEVEL, LOG_FORMAT, SKYNET_LOG_CONF_FILE


def get_log_path():
    try:
        with open(SKYNET_LOG_CONF_FILE) as f:
            line = ""
            while not line.startswith("LOG_FILE"):
                line = f.readline()
            log_file = line.split("=")[-1].strip()
    except IOError:
        log_file = DEFAULT_LOG_FILE

    try:
        os.mkdir(os.path.dirname(log_file))
    except OSError as e:
        if e.errno == errno.EEXIST:  # Failed as the file already exists.
            pass
        else:
            raise e
    with open(log_file, "a+") as f:
        pass
    return log_file


def get_log_level():
    try:
        with open(SKYNET_LOG_CONF_FILE) as f:
            line = ""
            while not line.startswith("LOG_LEVEL"):
                line = f.readline()
            log_level = line.split("=")[-1].strip()
    except IOError:
        log_level = DEFAULT_LOG_LEVEL
    return log_level


logger = logging.getLogger('skynetd')
handler = logging.FileHandler(get_log_path())
handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(handler)
logger.setLevel(logging.getLevelName(get_log_level()))
