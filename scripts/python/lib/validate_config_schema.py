#!/usr/bin/env python
"""Config schema validation"""

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
import logging
import jsonschema
from jsonschema import validate
import jsl

from lib.logger import Logger


def _string_int_field(**kwargs):
    return jsl.fields.AnyOfField(
        [
            jsl.fields.StringField(),
            jsl.fields.IntField()],
        **kwargs)


class Globals(jsl.Document):
    log_level = jsl.fields.StringField(required=True)
    introspection = jsl.fields.BooleanField()
    env_variables = jsl.fields.DictField()


class LocationRacks(jsl.Document):
    label = _string_int_field()
    room = _string_int_field()
    row = _string_int_field()
    cell = _string_int_field()


class Location(jsl.Document):
    time_zone = jsl.fields.StringField()
    data_center = _string_int_field()
    racks = jsl.fields.ArrayField(
        jsl.fields.DocumentField(LocationRacks))


class DeployerNetworks(jsl.Document):
    mgmt = jsl.fields.ArrayField(jsl.fields.DictField(
        properties={
            'device': jsl.fields.StringField(required=True),
            'interface_ipaddr': jsl.fields.IPv4Field(),
            'container_ipaddr': jsl.fields.IPv4Field(),
            'bridge_ipaddr': jsl.fields.IPv4Field(),
            'vlan': jsl.fields.IntField(),
            'netmask': jsl.fields.IPv4Field(),
            'prefix': jsl.fields.IntField()},
        additional_properties=False,
        required=True))
    client = jsl.fields.ArrayField(jsl.fields.DictField(
        properties={
            'type': jsl.fields.StringField(required=True),
            'device': jsl.fields.StringField(required=True),
            'container_ipaddr': jsl.fields.IPv4Field(required=True),
            'bridge_ipaddr': jsl.fields.IPv4Field(required=True),
            'vlan': jsl.fields.IntField(required=True),
            'netmask': jsl.fields.IPv4Field(),
            'prefix': jsl.fields.IntField()},
        additional_properties=False,
        required=True))


class Deployer(jsl.Document):
    gateway = jsl.fields.BooleanField()
    networks = jsl.DocumentField(DeployerNetworks)


class Interfaces(jsl.Document):
    label = jsl.fields.StringField()
    description = jsl.fields.StringField()
    iface = jsl.fields.StringField()
    address_start = jsl.fields.IPv4Field()
    address_list = jsl.fields.ArrayField()
    method = jsl.fields.StringField()
    dns_search = jsl.fields.StringField()
    dns_nameservers = jsl.fields.StringField()
    broadcast = jsl.fields.IPv4Field()
    netmask = jsl.fields.IPv4Field()
    gateway = jsl.fields.IPv4Field()
    mtu = jsl.fields.IntField()
    vlan_raw_device = jsl.fields.StringField()
    pre_up = jsl.fields.StringField()
    bridge_stp = jsl.fields.BooleanField()
    bridge_maxage = jsl.fields.IntField()
    bridge_fd = jsl.fields.IntField()
    bridge_ports = jsl.fields.StringField()
    bridge_hello = jsl.fields.IntField()
    bond_primary = jsl.fields.StringField()
    bond_master = jsl.fields.StringField()
    bond_mode = jsl.fields.StringField()
    bond_miimon = jsl.fields.IntField()
    bond_slaves = jsl.fields.StringField()
    DEVICE = jsl.fields.StringField()
    IPADDR_start = jsl.fields.IPv4Field()
    IPADDR_list = jsl.fields.ArrayField()
    BOOTPROTO = jsl.fields.StringField()
    SEARCH = jsl.fields.StringField()
    DNS1 = jsl.fields.IPv4Field()
    DNS2 = jsl.fields.IPv4Field()
    NETMASK = jsl.fields.IPv4Field()
    GATEWAY = jsl.fields.IPv4Field()
    BROADCAST = jsl.fields.IPv4Field()
    VLAN = jsl.fields.BooleanField()
    MTU = jsl.fields.IntField()
    STP = jsl.fields.BooleanField()
    MASTER = jsl.fields.StringField()
    BRIDGE = jsl.fields.StringField()
    BONDING_OPTS = jsl.fields.StringField()


class Networks(jsl.Document):
    label = jsl.fields.StringField()
    interfaces = jsl.fields.ArrayField(
        jsl.fields.StringField(),
        required=True)


class SoftwareBootstrap(jsl.Document):
    hosts = jsl.fields.StringField()
    executable = jsl.fields.StringField()
    command = jsl.fields.StringField()


class SchemaDefinition(jsl.Document):
    version = jsl.fields.StringField(required=True)

    globals = jsl.fields.DocumentField(Globals)

    location = jsl.fields.DocumentField(Location)

    deployer = jsl.DocumentField(Deployer)

    switches = jsl.fields.DictField(required=True)

    interfaces = jsl.fields.ArrayField(
        jsl.fields.DocumentField(Interfaces),
        required=True)

    networks = jsl.fields.ArrayField(
        jsl.fields.DocumentField(Networks),
        required=True)

    node_templates = jsl.fields.ArrayField(required=True)

    software_bootstrap = jsl.fields.ArrayField(
        jsl.fields.DocumentField(SoftwareBootstrap))


class ValidateConfigSchema(object):
    """Config schema validation

    Args:
        config (object): Config
    """

    def __init__(self, config):
        self.log = logging.getLogger(Logger.LOG_NAME)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        self.log.addHandler(ch)
        self.config = config

    def validate_config_schema(self):
        """Config schema validation

        Exception:
            If schema validation fails
        """

        schema = SchemaDefinition.get_schema(ordered=True)
        try:
            validate(
                self.config, schema, format_checker=jsonschema.FormatChecker())
        except jsonschema.exceptions.ValidationError as error:
            self.log.error('Schema validation failed:' + '\n' +
                           'Config file section: ' + str(error.path[0]) + ':' +
                           '\n' + str(error.message))
            sys.exit(1)
        self.log.info('Config schema validation completed successfully')
