# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import re

from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon.templatetags.sizeformat import filesizeformat, float_format


LOG = logging.getLogger(__name__)


class StringWithPlusOperation(str):
    """
    Override "+" operation for string object.
    It's used to get summary of numbers(string format) in usage tables.
    eg: "600 KB" + "600 KB" = "1.1 MB".
    The plus operation is done by `sum` function with
    column property `summation` set tu 'sum'.
    """
    def __init__(self, *args, **kwargs):
        super(StringWithPlusOperation, self).__init__(*args, **kwargs)

    def _split_str(self, string):
        """
        Split a string to two parts.
        The first group is the float number and
        the second one is a string like unit name.
        """
        result = re.search(r'^([-+]?[0-9]*\.?[0-9]+)(.*)$', string)
        if result:
            number = float(result.groups()[0])
            unit = result.groups()[1]
            return number, unit
        return None, None

    # given a number and units, convert that to bytes
    def to_bytes(self, number, unit):
        if unit == "PB":
            result_bytes = number * (1024 * 1024 * 1024 * 1024 * 1024)
        elif unit == "TB":
            result_bytes = number * (1024 * 1024 * 1024 * 1024)
        elif unit == "GB":
            result_bytes = number * (1024 * 1024 * 1024)
        elif unit == "MB":
            result_bytes = number * (1024 * 1024)
        elif unit == "KB":
            result_bytes = number * (1024)
        else:
            result_bytes = number

        return result_bytes

    def __radd__(self, another):
        num_x, unit_x = self._split_str(self)
        num_y = 0
        unit_y = ""

        if isinstance(another, (int, float)):
            num_y = another
        elif isinstance(another, basestring):
            num_y, unit_y = self._split_str(another)
        elif isinstance(another, self.__class__):
            num_y, unit_y = self._split_str(another.__str__())

        if num_y is None or num_x is None:
            return '-'

        unit_x = unit_x.strip()
        unit_y = unit_y.strip()

        if unit_x == unit_y:
            return "%s%s" % (num_x + num_y, unit_x)
        else:
            # convert both units to bytes
            converted_num_x = self.to_bytes(num_x, unit_x)
            converted_num_y = self.to_bytes(num_y, unit_y)

            total = converted_num_x + converted_num_y
            result = filesizeformat(total, float_format)
            return result


class CommonFilterAction(tables.FilterAction):
    """
    Since server-side filter action is disabled and
    client-side filter is superior, this class is just
    a common class to enable client-side js filter action.
    """
    def filter(self, table, tenants, filter_string):
        q = filter_string.lower()

        def comp(tenant):
            if q in tenant.name.lower():
                return True
            return False

        return filter(comp, tenants)


def get_bytes(field_name=""):
    def transform(sample):
        field = getattr(sample, field_name, None)
        result = filesizeformat(field, float_format)
        return StringWithPlusOperation(result)
    return transform


class DiskUsageTable(tables.DataTable):
    tenant = tables.Column("tenant", verbose_name=_("Tenant"), sortable=True)
    user = tables.Column("user", verbose_name=_("User"), sortable=True)
    instance = tables.Column("resource",
                             verbose_name=_("Resource"),
                             sortable=True)
    disk_read_bytes = tables.Column(get_bytes("disk_read_bytes"),
                                    verbose_name=_("Disk Read Bytes"),
                                    summation="sum",
                                    sortable=True)
    disk_read_requests = tables.Column("disk_read_requests",
                                       verbose_name=_("Disk Read Requests"),
                                       summation="sum",
                                       sortable=True)
    disk_write_bytes = tables.Column(get_bytes("disk_write_bytes"),
                                     verbose_name=_("Disk Write Bytes"),
                                     summation="sum",
                                     sortable=True)
    disk_write_requests = tables.Column("disk_write_requests",
                                        verbose_name=_("Disk Write Requests"),
                                        summation="sum",
                                        sortable=True)

    def get_object_id(self, datum):
        return datum.tenant + datum.user + datum.resource

    class Meta:
        name = "global_disk_usage"
        verbose_name = _("Global Disk Usage")
        table_actions = (CommonFilterAction,)
        multi_select = False


class NetworkTrafficUsageTable(tables.DataTable):
    tenant = tables.Column("tenant", verbose_name=_("Tenant"))
    user = tables.Column("user", verbose_name=_("User"), sortable=True)
    instance = tables.Column("resource",
                             verbose_name=_("Resource"),
                             sortable=True)
    network_incoming_bytes = tables.Column(get_bytes("network_incoming_bytes"),
                                   verbose_name=_("Network incoming Bytes"),
                                   summation="sum",
                                   sortable=True)
    network_incoming_packets = tables.Column("network_incoming_packets",
                            verbose_name=_("Network incoming Packets"),
                            summation="sum", sortable=True)
    network_outgoing_bytes = tables.Column(get_bytes("network_outgoing_bytes"),
                            verbose_name=_("Network Outgoing Bytes"),
                            summation="sum", sortable=True)
    network_outgoing_packets = tables.Column("network_outgoing_packets",
                            verbose_name=_("Network Outgoing Packets"),
                            summation="sum", sortable=True)

    def get_object_id(self, datum):
        return datum.tenant + datum.user + datum.resource

    class Meta:
        name = "global_network_traffic_usage"
        verbose_name = _("Global Network Traffic Usage")
        table_actions = (CommonFilterAction,)
        multi_select = False


class NetworkUsageTable(tables.DataTable):
    tenant = tables.Column("tenant", verbose_name=_("Tenant"))
    user = tables.Column("user", verbose_name=_("User"), sortable=True)
    instance = tables.Column("resource",
                             verbose_name=_("Resource"),
                             sortable=True)
    network_duration = tables.Column("network",
                                   verbose_name=_("Network Duration"),
                                   summation="sum",
                                   sortable=True)
    network_creation_requests = tables.Column("network_create",
                            verbose_name=_("Network Creation Requests"),
                            summation="sum", sortable=True)
    subnet_duration = tables.Column("subnet",
                            verbose_name=_("Subnet Duration"),
                            summation="sum", sortable=True)
    subnet_creation = tables.Column("subnet_create",
                            verbose_name=_("Subnet Creation Requests"),
                            summation="sum", sortable=True)
    port_duration = tables.Column("port",
                            verbose_name=_("Port Duration"),
                            summation="sum", sortable=True)
    port_creation = tables.Column("port_create",
                            verbose_name=_("Port Creation Requests"),
                            summation="sum", sortable=True)
    router_duration = tables.Column("router",
                            verbose_name=_("Router Duration"),
                            summation="sum", sortable=True)
    router_creation = tables.Column("router_create",
                            verbose_name=_("Router Creation Requests"),
                            summation="sum", sortable=True)
    port_duration = tables.Column("port",
                            verbose_name=_("Port Duration"),
                            summation="sum", sortable=True)
    port_creation = tables.Column("port_create",
                            verbose_name=_("Port Creation Requests"),
                            summation="sum", sortable=True)
    ip_floating_duration = tables.Column("ip_floating",
                            verbose_name=_("Floating IP Duration"),
                            summation="sum", sortable=True)
    ip_floating_creation = tables.Column("ip_floating_create",
                            verbose_name=_("Floating IP Creation Requests"),
                            summation="sum", sortable=True)

    def get_object_id(self, datum):
        return "%s%s%s" % (datum.tenant,
                           datum.user,
                           datum.resource)

    class Meta:
        name = "global_network_usage"
        verbose_name = _("Global Network Usage")
        table_actions = (CommonFilterAction,)
        multi_select = False


class ObjectStoreUsageTable(tables.DataTable):
    tenant = tables.Column("tenant", verbose_name=_("Tenant"))
    user = tables.Column("user", verbose_name=_("User"), sortable=True)
    resource = tables.Column("resource",
                             verbose_name=_("Resource"),
                             sortable=True)
    storage_incoming_bytes = tables.Column(
                           get_bytes("storage_objects_incoming_bytes"),
                           verbose_name=_("Object Storage Incoming Bytes"),
                           summation="sum", sortable=True)
    storage_outgoing_bytes = tables.Column(
                            get_bytes("storage_objects_outgoing_bytes"),
                            verbose_name=_("Object Storage Outgoing Bytes"),
                            summation="sum", sortable=True)
    storage_objects = tables.Column("storage_objects",
                            verbose_name=_("Total Number of Objects"),
                            summation="sum", sortable=True)
    storage_objects_size = tables.Column(get_bytes("storage_objects_size"),
                            verbose_name=_("Total Size of Objects "),
                            summation="sum", sortable=True)

    def get_object_id(self, datum):
        return "%s%s%s" % (datum.tenant,
                           datum.user,
                           datum.resource)

    class Meta:
        name = "global_object_store_usage"
        verbose_name = _("Global Object Store Usage")
        table_actions = (CommonFilterAction,)
        multi_select = False
