#!/usr/bin/env python
# Copyright 2017 IBM Corp.
#
# All Rights Reserved.
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

from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import xmlrpclib

from lib.logger import Logger

COBBLER_USER = 'cobbler'
COBBLER_PASS = 'cobbler'


class CobblerSetNetbootEnabled(object):
    def __init__(self, log, netboot_enabled_value):
        cobbler_server = xmlrpclib.Server("http://127.0.0.1/cobbler_api")
        token = cobbler_server.login(COBBLER_USER, COBBLER_PASS)

        for system in cobbler_server.get_systems():
            name = system['name']

            handle = cobbler_server.get_system_handle(name, token)
            cobbler_server.modify_system(
                handle, "netboot_enabled", netboot_enabled_value, token)
            cobbler_server.save_system(handle, token)

            log.info(
                "Cobbler Modify System: name=%s netboot_enabled=%s" %
                (name, netboot_enabled_value))


if __name__ == '__main__':
    """
    Arg1: netboot_enabled value
    Arg2: log level
    """
    LOG = Logger(__file__)

    ARGV_MAX = 3
    ARGV_COUNT = len(sys.argv)
    if ARGV_COUNT > ARGV_MAX:
        try:
            raise Exception()
        except:
            LOG.error('Invalid argument count')
            sys.exit(1)

    NETBOOT_ENABLED_VALUE = sys.argv[1]
    LOG.set_level(sys.argv[2])

    CobblerSetNetbootEnabled(LOG, NETBOOT_ENABLED_VALUE)
