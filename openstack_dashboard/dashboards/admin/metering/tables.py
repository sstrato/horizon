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

from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon.templatetags.sizeformat import filesizeformat
from horizon.templatetags.sizeformat import float_format
from openstack_dashboard import api


LOG = logging.getLogger(__name__)


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
        return filesizeformat(field, float_format)
    return transform


def get_status(fields):
    def transform(datum):
        if any([datum.get(field) is 0 or datum.get(field)
                for field in fields]):
            return "up"
        else:
            return "none"
    return transform


class GlobalDiskUsageUpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, object_id):
        """
        The object_id is like this:
            "<user_id>__<tenant_id>__<reousrce_id>".
        """
        user, tenant, resource = object_id.split("__")
        return api.ceilometer.global_disk_usage_get(request,
                                                    user,
                                                    tenant,
                                                    resource)


class GlobalDiskUsageTable(tables.DataTable):
    tenant = tables.Column("tenant", verbose_name=_("Tenant"), sortable=True)
    user = tables.Column("user", verbose_name=_("User"), sortable=True)
    status = tables.Column(get_status(["disk.read.bytes",
                                       "disk.write.bytes",
                                       "disk.read.requests",
                                       "disk.write.requests"
                                       ]),
                           verbose_name=_("Status"),
                           hidden=True)
    instance = tables.Column("resource",
                             verbose_name=_("Resource"),
                             sortable=True)
    disk_read_bytes = tables.Column(get_bytes("disk.read.bytes"),
                                    verbose_name=_("Disk Read Bytes"),
                                    sortable=True)
    disk_read_requests = tables.Column("disk.read.requests",
                                       verbose_name=_("Disk Read Requests"),
                                       sortable=True)
    disk_write_bytes = tables.Column(get_bytes("disk.write.bytes"),
                                     verbose_name=_("Disk Write Bytes"),
                                     sortable=True)
    disk_write_requests = tables.Column("disk.write.requests",
                                        verbose_name=_("Disk Write Requests"),
                                        sortable=True)

    def get_object_id(self, datum):
        return "%s__%s__%s" % (datum.user,
                               datum.tenant,
                               datum.resource)

    class Meta:
        name = "global_disk_usage"
        verbose_name = _("Global Disk Usage")
        status_columns = ["status"]
        table_actions = (CommonFilterAction,)
        row_class = GlobalDiskUsageUpdateRow
        multi_select = False


class GlobalNetworkTrafficUsageUpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, object_id):
        """
        The object_id is like this:
            "<user_id>__<tenant_id>__<reousrce_id>".
        """
        user, tenant, resource = object_id.split("__")
        return api.ceilometer\
                .global_network_traffic_usage_get(request,
                                                  user,
                                                  tenant,
                                                  resource)


class GlobalNetworkTrafficUsageTable(tables.DataTable):
    tenant = tables.Column("tenant", verbose_name=_("Tenant"))
    user = tables.Column("user", verbose_name=_("User"), sortable=True)
    status = tables.Column(get_status(["network.incoming.bytes",
                                       "network.incoming.packets",
                                       "network.outgoing.bytes",
                                       "network.outgoing.packets"]),
                           verbose_name=_("Status"),
                           hidden=True)
    instance = tables.Column("resource",
                             verbose_name=_("Resource"),
                             sortable=True)
    network_incoming_bytes = tables\
            .Column(get_bytes("network.incoming.bytes"),
                    verbose_name=_("Network incoming Bytes"),
                    sortable=True)
    network_incoming_packets = tables\
            .Column("network.incoming.packets",
                    verbose_name=_("Network incoming Packets"),
                    sortable=True)
    network_outgoing_bytes = tables\
            .Column(get_bytes("network.outgoing.bytes"),
                    verbose_name=_("Network Outgoing Bytes"),
                    sortable=True)
    network_outgoing_packets = tables\
            .Column("network.outgoing.packets",
                    verbose_name=_("Network Outgoing Packets"),
                    sortable=True)

    def get_object_id(self, datum):
        return "%s__%s__%s" % (datum.user,
                               datum.tenant,
                               datum.resource)

    class Meta:
        name = "global_network_traffic_usage"
        verbose_name = _("Global Network Traffic Usage")
        table_actions = (CommonFilterAction,)
        row_class = GlobalNetworkTrafficUsageUpdateRow
        status_columns = ["status"]
        multi_select = False


class GlobalNetworkUsageUpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, object_id):
        """
        The object_id is like this:
            "<user_id>__<tenant_id>__<reousrce_id>".
        """
        user, tenant, resource = object_id.split("__")
        return api.ceilometer.global_network_usage_get(request,
                                                       user,
                                                       tenant,
                                                       resource)


class GlobalNetworkUsageTable(tables.DataTable):
    tenant = tables.Column("tenant", verbose_name=_("Tenant"))
    user = tables.Column("user", verbose_name=_("User"), sortable=True)
    status = tables.Column(get_status(["network", "network_create",
                                       "subnet", "subnet_create",
                                       "port", "port_create",
                                       "router", "router_create",
                                       "ip_floating", "ip_floating_create"]),
                           verbose_name=_("Status"),
                           hidden=True)
    instance = tables.Column("resource",
                             verbose_name=_("Resource"),
                             sortable=True)
    network_duration = tables.Column("network",
                                     verbose_name=_("Network Duration"),
                                     sortable=True)
    network_creation_requests = tables\
            .Column("network_create",
                    verbose_name=_("Network Creation Requests"),
                    sortable=True)
    subnet_duration = tables.Column("subnet",
                                    verbose_name=_("Subnet Duration"),
                                    sortable=True)
    subnet_creation = tables.Column("subnet_create",
                                    verbose_name=_("Subnet Creation Requests"),
                                    sortable=True)
    port_duration = tables.Column("port",
                                  verbose_name=_("Port Duration"),
                                  sortable=True)
    port_creation = tables.Column("port_create",
                                  verbose_name=_("Port Creation Requests"),
                                  sortable=True)
    router_duration = tables.Column("router",
                                    verbose_name=_("Router Duration"),
                                    sortable=True)
    router_creation = tables.Column("router_create",
                                    verbose_name=_("Router Creation Requests"),
                                    sortable=True)
    port_duration = tables.Column("port",
                                  verbose_name=_("Port Duration"),
                                  sortable=True)
    port_creation = tables.Column("port_create",
                                  verbose_name=_("Port Creation Requests"),
                                  sortable=True)
    ip_floating_duration = tables\
            .Column("ip_floating",
                    verbose_name=_("Floating IP Duration"),
                    sortable=True)
    ip_floating_creation = tables\
            .Column("ip_floating_create",
                    verbose_name=_("Floating IP Creation Requests"),
                    sortable=True)

    def get_object_id(self, datum):
        return "%s__%s__%s" % (datum.user,
                               datum.tenant,
                               datum.resource)

    class Meta:
        name = "global_network_usage"
        verbose_name = _("Global Network Usage")
        table_actions = (CommonFilterAction,)
        row_class = GlobalNetworkUsageUpdateRow
        status_columns = ["status"]
        multi_select = False


class GlobalObjectStoreUsageUpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, object_id):
        """
        The object_id is like this:
            "<user_id>__<tenant_id>__<reousrce_id>".
        """
        user, tenant, resource = object_id.split("__")
        return api.ceilometer.global_object_store_usage_get(request,
                                                            user,
                                                            tenant,
                                                            resource)


class GlobalObjectStoreUsageTable(tables.DataTable):
    tenant = tables.Column("tenant", verbose_name=_("Tenant"))
    user = tables.Column("user", verbose_name=_("User"), sortable=True)
    status = tables.Column(get_status(["storage.objects",
                                       "storage.objects.size",
                                       "storage.objects.incoming.bytes",
                                       "storage.objects.outgoing.bytes"]),
                           verbose_name=_("Status"),
                           hidden=True)
    resource = tables.Column("resource",
                             verbose_name=_("Resource"),
                             sortable=True)
    storage_incoming_bytes = tables.Column(
                           get_bytes("storage.objects.incoming.bytes"),
                           verbose_name=_("Object Storage Incoming Bytes"),
                           sortable=True)
    storage_outgoing_bytes = tables.Column(
                            get_bytes("storage.objects.outgoing.bytes"),
                            verbose_name=_("Object Storage Outgoing Bytes"),
                            sortable=True)
    storage_objects = tables.Column("storage.objects",
                            verbose_name=_("Total Number of Objects"),
                            sortable=True)
    storage_objects_size = tables.Column(get_bytes("storage_objects_size"),
                            verbose_name=_("Total Size of Objects "),
                            sortable=True)

    def get_object_id(self, datum):
        return "%s__%s__%s" % (datum.user,
                               datum.tenant,
                               datum.resource)

    class Meta:
        name = "global_object_store_usage"
        verbose_name = _("Global Object Store Usage")
        table_actions = (CommonFilterAction,)
        row_class = GlobalObjectStoreUsageUpdateRow
        status_columns = ["status"]
        multi_select = False
