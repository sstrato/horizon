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

import itertools
import logging

from ceilometerclient import client as ceilometer_client
from django.conf import settings

from .base import APIDictWrapper
from .base import APIResourceWrapper
from .base import url_for

import keystone


LOG = logging.getLogger(__name__)


class Meter(APIResourceWrapper):
    _attrs = ['name', 'type', 'unit', 'resource_id', 'user_id',
              'project_id']


class Resource(APIResourceWrapper):
    _attrs = ['resource_id', "source", "user_id", "project_id", "metadata"]

    @property
    def name(self):
        name = self.metadata.get("name", None)
        display_name = self.metadata.get("display_name", None)
        return name or display_name or ""


class Sample(APIResourceWrapper):
    _attrs = ['counter_name', 'user_id', 'resource_id', 'timestamp',
              'resource_metadata', 'source', 'counter_unit', 'counter_volume',
              'project_id', 'counter_type', 'resource_metadata']

    @property
    def instance(self):
        if 'display_name' in self.resource_metadata:
            return self.resource_metadata['display_name']
        elif 'instance_id' in self.resource_metadata:
            return self.resource_metadata['instance_id']
        else:
            return None

    @property
    def name(self):
        name = self.resource_metadata.get("name", None)
        display_name = self.resource_metadata.get("display_name", None)
        return name or display_name or ""


class GlobalObjectStoreUsage(APIDictWrapper):
    _attrs = ["id", "tenant", "user", "resource", "storage_objects",
              "storage_objects_size", "storage_objects_outgoing_bytes",
              "storage_objects_incoming_bytes"]


class GlobalDiskUsage(APIDictWrapper):
    _attrs = ["id", "tenant", "user", "resource", "disk_read_bytes",
              "disk_read_requests", "disk_write_bytes",
              "disk_write_requests"]


class GlobalNetworkTrafficUsage(APIDictWrapper):
    _attrs = ["id", "tenant", "user", "resource", "network_incoming_bytes",
              "network_incoming_packets", "network_outgoing_bytes",
              "network_outgoing_packets"]


class GlobalNetworkUsage(APIDictWrapper):
    _attrs = ["id", "tenant", "user", "resource", "network", "network_create",
              "subnet", "subnet_create", "port", "port_create", "router",
              "router_create", "ip_floating", "ip_floating_create"]


class Statistic(APIResourceWrapper):
    _attrs = ['period', 'period_start', 'period_end',
              'count', 'min', 'max', 'sum', 'avg',
              'duration', 'duration_start', 'duration_end']


def ceilometerclient(request):
    endpoint = url_for(request, 'metering')
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    LOG.debug('ceilometerclient connection created using token "%s" '
              'and endpoint "%s"' % (request.user.token.id, endpoint))
    return ceilometer_client.Client('2', endpoint, token=request.user.token.id,
                                    insecure=insecure)


def sample_list(request, meter_name, query=[]):
    """List the samples for this meters."""
    samples = ceilometerclient(request).samples.list(meter_name=meter_name,
                                                     q=query)
    return [Sample(s) for s in samples]


def meter_list(request, query=[]):
    """List the user's meters."""
    meters = ceilometerclient(request).meters.list(query)
    return [Meter(m) for m in meters]


def resource_list(request, query=[]):
    """List the resources."""
    resources = ceilometerclient(request).\
        resources.list(q=query)
    return [Resource(r) for r in resources]


def statistic_list(request, meter_name, query=[]):
    statistics = ceilometerclient(request).\
        statistics.list(meter_name=meter_name, q=query)
    return [Statistic(s) for s in statistics]


def global_object_store_usage(request):
    result_list = global_usage_preload(request,
                                       ["storage.objects",
                                        "storage.objects.size",
                                        "storage.objects.incoming.bytes",
                                        "storage.objects.outgoing.bytes"])
    return [GlobalObjectStoreUsage(u) for u in result_list]


def global_object_store_usage_get(request, usage_id):
    meter_names = ["storage.objects",
                   "storage.objects.size",
                   "storage.objects.incoming.bytes",
                   "storage.objects.outgoing.bytes"]
    usage = global_usage_get(request, meter_names, usage_id)
    return GlobalObjectStoreUsage(usage)


def global_disk_usage(request):
    result_list = global_usage_preload(request, ["disk.read.bytes",
                                                 "disk.read.requests",
                                                 "disk.write.bytes",
                                                 "disk.write.requests"])
    return [GlobalDiskUsage(u) for u in result_list]


def global_disk_usage_get(request, usage_id):
    meter_names = ["disk.read.bytes",
                   "disk.read.requests",
                   "disk.write.bytes",
                   "disk.write.requests"]
    usage = global_usage_get(request, meter_names, usage_id)
    return GlobalDiskUsage(usage)


def global_network_traffic_usage(request):
    result_list = global_usage_preload(request, ["network.incoming.bytes",
                                                 "network.incoming.packets",
                                                 "network.outgoing.bytes",
                                                 "network.outgoing.packets"])
    return [GlobalNetworkTrafficUsage(u) for u in result_list]


def global_network_traffic_usage_get(request, usage_id):
    meter_names = ["network.incoming.bytes",
                   "network.incoming.packets",
                   "network.outgoing.bytes",
                   "network.outgoing.packets"]
    usage = global_usage_get(request, meter_names, usage_id)
    return GlobalNetworkTrafficUsage(usage)


def global_network_usage(request):
    result_list = global_usage_preload(request,
                                       ["network", "network_create",
                                        "subnet", "subnet_create",
                                        "port", "port_create",
                                        "router", "router_create",
                                        "ip_floating", "ip_floating_create"])
    return [GlobalNetworkUsage(u) for u in result_list]


def global_network_usage_get(request, usage_id):
    meter_names = ["network", "network_create",
                   "subnet", "subnet_create",
                   "port", "port_create",
                   "router", "router_create",
                   "ip_floating", "ip_floating_create"]
    usage = global_usage_get(request, meter_names, usage_id)
    return GlobalNetworkUsage(usage)


def global_usage_get(request, meter_names, usage_id):
    try:
        tenant_id, user_id, resource_id = usage_id.split("__")
    except ValueError:
        return []

    query = []
    if user_id and user_id != 'None':
        query.append({"field": "user", "op": "eq", "value": user_id})
    if tenant_id and tenant_id != 'None':
        query.append({"field": "project", "op": "eq", "value": tenant_id})
    if resource_id and resource_id != 'None':
        query.append({"field": "resource", "op": "eq", "value": resource_id})

    usage_list = []
    usage = dict(id=usage_id,
                 tenant=CachedResources.get_tenant_name(request,
                                                        tenant_id),
                 user=CachedResources.get_user_name(request,
                                                    user_id),
                 resource=resource_id)
    for meter in meter_names:
        statistics = statistic_list(request, meter,
                                    query=query)
        meter = meter.replace(".", "_")
        if statistics:
            usage.setdefault(meter, statistics[0].max)
        else:
            usage.setdefault(meter, 0)

        usage_list.append(usage)

    usage_list = itertools.groupby(
        usage_list,
        lambda x: x["id"],
    )
    usage_list = map(lambda x: list(x[1]), usage_list)
    usage_list = reduce(lambda x, y: x.update(y) or x, usage_list)
    return usage_list[0]


def global_usage_preload(request, fields):
    """
    Get "user", "tenant", "resource" for a horizon table datum
    without actually data.
    The data will be loaded asynchronously via ``global_usage_get``.
    """
    meters = CachedResources.get_meter_list(request)

    filtered = filter(lambda m: m.name in fields, meters)

    usage_list = []
    for m in filtered:
        usage_list.append({
            "id": "%s__%s__%s" % (m.project_id, m.user_id, m.resource_id),
            "tenant": CachedResources.get_tenant_name(request,
                                                      m.project_id),
            "user": CachedResources.get_user_name(request,
                                                  m.user_id),
            "resource": m.resource_id
        })
    # To remove redundent usage.
    tupled_usage_list = [tuple(d.items()) for d in usage_list]
    unique_usage_list = [dict(t) for t in set(tupled_usage_list)]
    return unique_usage_list


class CachedResources(object):
    """
    Cached users, tenants and meters.
    """
    _users = None
    _tenants = None
    _meters = None

    @classmethod
    def get_meter_list(cls, request, query=None):
        if not cls._meters:
            cls._meters = meter_list(request, query)
        return cls._meters

    @classmethod
    def get_user_name(cls, request, user_id):
        if not cls._users:
            cls._users = keystone.user_list(request)
        for u in cls._users:
            if u.id == user_id:
                return u.name
        return None

    @classmethod
    def get_tenant_name(cls, request, tenant_id):
        if not cls._tenants:
            cls._tenants, more = keystone.tenant_list(request)
        for t in cls._tenants:
            if t.id == tenant_id:
                return t.name
        return None
