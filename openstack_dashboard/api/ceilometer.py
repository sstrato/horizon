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
import urlparse

from django.conf import settings
from ceilometerclient import client as ceilometer_client

from horizon import exceptions

from .base import APIResourceWrapper, url_for

import keystone

LOG = logging.getLogger(__name__)


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


def ceilometerclient(request):
    o = urlparse.urlparse(url_for(request, 'metering'))
    url = "://".join((o.scheme, o.netloc))
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    LOG.debug('ceilometerclient connection created using token "%s" '
              'and url "%s"' % (request.user.token.id, url))
    return ceilometer_client.Client('1', url, token=request.user.token.id,
                             insecure=insecure)


def sample_list(request, counter_name, resource_id=None, user_id=None,
                tenant_id=None, start_timestamp=None, end_timestamp=None,
                metaquery='', source="openstack"):
    """List the samples for this meters."""
    try:
        samples = ceilometerclient(request).\
            samples.list(counter_name=counter_name,
                         resource_id=resource_id,
                         user_id=user_id,
                         tenant_id=tenant_id,
                         start_timestamp=start_timestamp,
                         end_timestamp=end_timestamp,
                         metaquery=metaquery,
                         source=source)
    except:
        samples = []
        LOG.exception("Ceilometer sapmles not found: %s" % counter_name)
        exceptions.handle(request)

    return [Sample(s) for s in samples]


def meter_list(request, resource_id, user_id, tenant_id, source):
    """List the user's meters."""
    meters = ceilometerclient(request).meters.list(resource_id=resource_id,
                                                   user_id=user_id,
                                                   tenant_id=tenant_id,
                                                   source=source)
    return meters


def user_list(request):
    """List the users."""
    users = ceilometerclient(request).users.list()
    return users


def resource_list(request, source, user_id):
    """List the resources."""
    resources = ceilometerclient(request).\
        resources.list(source=source, user_id=user_id)
    return resources


def tenant_list(request, source):
    tenants = ceilometerclient(request).tenants.list(source=source)
    return tenants


def disk_io(request):
    read_bytes = get_total_volume(sample_list(request, "disk.read.bytes"))
    write_bytes = get_total_volume(sample_list(request, "disk.write.bytes"))
    read_requests = get_total_volume(sample_list(request,
                                                 "disk.read.requests"))
    write_requests = get_total_volume(sample_list(request,
                                                  "disk.write.requests"))

    usage = merge_samples(read_bytes + write_bytes +
                             read_requests + write_requests)
    keystone_tenant_list = keystone.tenant_list(request)
    keystone_user_list = keystone.user_list(request)
    for u in usage:
        for t in keystone_tenant_list:
            if t.id == u.project_id:
                u.tenant = t.name
        for ks_user in keystone_user_list:
            if ks_user.id == u.user_id:
                u.user = ks_user.name
    return usage


def network_io(request):
    incoming_bytes = get_total_volume(sample_list(request,
                                                  "network.incoming.bytes"))
    outgoing_bytes = get_total_volume(sample_list(request,
                                                  "network.outgoing.bytes"))
    incoming_packets = get_total_volume(sample_list(request,
                                                  "network.incoming.packets"))
    outgoing_packets = get_total_volume(sample_list(request,
                                                  "network.outgoing.packets"))

    usage = merge_samples(incoming_bytes + incoming_packets +
                          outgoing_bytes + outgoing_packets)
    keystone_tenant_list = keystone.tenant_list(request)
    keystone_user_list = keystone.user_list(request)
    for u in usage:
        for t in keystone_tenant_list:
            if t.id == u.project_id:
                u.tenant = t.name
        for ks_user in keystone_user_list:
            if ks_user.id == u.user_id:
                u.user = ks_user.name
    return usage


def merge_samples(sample_list):
    """
    Merge multiple sample lists to one list using combination
    of ``resource_id``, ``user_id`` and ``project_id`` as keys.
    """
    result = {}
    for sample in sample_list:
        key = "%s_%s_%s" % (sample.resource_id,
                            sample.user_id, sample.project_id)
        counter_name = sample.counter_name.replace(".", "_")
        if key in result:
            setattr(result[key], counter_name, sample.counter_volume)
        else:
            setattr(sample, counter_name, sample.counter_volume)
            result[key] = sample
    return result.values()


def get_total_volume(sample_list):
    """
    Get total volume of counter in a sample list.
    It merges itmes which have the same ``resource_id``,
    ``user_id``, ``project_id``.
    """
    result = {}
    for sample in sample_list:
        key = "%s_%s_%s" % (sample.resource_id,
                            sample.user_id, sample.project_id)
        if key in result:
            result[key].counter_volume += sample.counter_volume
        else:
            result[key] = sample
    return result.values()
