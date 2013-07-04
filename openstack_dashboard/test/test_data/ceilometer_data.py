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

from ceilometerclient.v2.meters import Meter
from ceilometerclient.v2.meters import MeterManager
from ceilometerclient.v2.resources import Resource
from ceilometerclient.v2.resources import ResourceManager
from ceilometerclient.v2.statistics import Statistics
from ceilometerclient.v2.statistics import StatisticsManager
from ceilometerclient.v2.samples import Sample
from ceilometerclient.v2.samples import SampleManager

from openstack_dashboard.api.ceilometer import GlobalDiskUsage
from openstack_dashboard.api.ceilometer import GlobalNetworkTrafficUsage
from openstack_dashboard.api.ceilometer import GlobalNetworkUsage
from openstack_dashboard.api.ceilometer import GlobalObjectStoreUsage

from .utils import TestDataContainer


def data(TEST):
    TEST.resources = TestDataContainer()
    TEST.samples = TestDataContainer()
    TEST.meters = TestDataContainer()
    TEST.statistics = TestDataContainer()
    TEST.global_disk_usages = TestDataContainer()
    TEST.global_network_usages = TestDataContainer()
    TEST.global_network_traffic_usages = TestDataContainer()
    TEST.global_object_store_usages = TestDataContainer()

    # global disk usage
    global_disk_usage_1 = dict(
        tenant="tenant_1",
        user="user1",
        resource="resource1",
        disk_read_bytes="disk_read_bytes1",
        disk_write_bytes="disk_write_bytes1",
        disk_read_requests="disk_read_requests1",
        disk_write_requests="disk_write_requests1",)
    global_disk_usage_2 = dict(
        tenant="tenant_2",
        user="user2",
        resource="resource2",
        disk_read_bytes="disk_read_bytes2",
        disk_write_bytes="disk_write_bytes2",
        disk_read_requests="disk_read_requests2",
        disk_write_requests="disk_write_requests2",)
    TEST.global_disk_usages.add(GlobalDiskUsage(global_disk_usage_1))
    TEST.global_disk_usages.add(GlobalDiskUsage(global_disk_usage_2))

    # global network traffic usage
    global_network_traffic_usage_1 = dict(
        tenant="tenant_1",
        user="user1",
        resource="resource1",
        network_incoming_bytes="network_incoming_bytes1",
        network_incoming_packets="network_incoming_packets1",
        network_outgoing_bytes="network_outgoing_bytes1",
        network_outgoing_packets="network_outgoing_packets1",)
    global_network_traffic_usage_2 = dict(
        tenant="tenant_2",
        user="user2",
        resource="resource2",
        network_incoming_bytes="network_incoming_bytes2",
        network_incoming_packets="network_incoming_packets2",
        network_outgoing_bytes="network_outgoing_bytes2",
        network_outgoing_packets="network_outgoing_packets2",)
    TEST.global_network_traffic_usages\
        .add(GlobalNetworkTrafficUsage(global_network_traffic_usage_1))
    TEST.global_network_traffic_usages\
        .add(GlobalNetworkTrafficUsage(global_network_traffic_usage_2))

    global_network_usage_1 = dict(
      tenant="tenant_1",
      user="user_1",
      resource="resource_id_1",
      network=2,
      network_create=2,
      subnet=2,
      subnet_create=2,
      port=2,
      port_create=2,
      router=2,
      router_create=2,
      ip_floating=2,
      ip_floating_create=2)
    global_network_usage_2 = dict(
      tenant="tenant_2",
      user="user_2",
      resource="resource_id_2",
      network=2,
      network_create=2,
      subnet=2,
      subnet_create=2,
      port=2,
      port_create=2,
      router=2,
      router_create=2,
      ip_floating=2,
      ip_floating_create=2)
    TEST.global_network_usages.add(GlobalNetworkUsage(global_network_usage_1))
    TEST.global_network_usages.add(GlobalNetworkUsage(global_network_usage_2))

    global_object_store_usage_1 = dict(
      tenant="tenant_1",
      user="user_1",
      resource="resource_id_1",
      storage_objects=1,
      storage_objects_size=1,
      storage_objects_outgoing_bytes=1,
      storage_objects_incoming_bytes=1
    )
    global_object_store_usage_2 = dict(
      tenant="tenant_2",
      user="user_2",
      resource="resource_id_2",
      storage_objects=2,
      storage_objects_size=2,
      storage_objects_outgoing_bytes=2,
      storage_objects_incoming_bytes=2
    )
    TEST.global_object_store_usages\
      .add(GlobalObjectStoreUsage(global_object_store_usage_1))
    TEST.global_object_store_usages\
      .add(GlobalObjectStoreUsage(global_object_store_usage_2))

    # resources
    resource_dict_1 = dict(
        resource_id='fake_resource_id',
        project_id='fake_project_id',
        user_id="fake_user_id",
        timestamp='2012-07-02T10:42:00.000000',
        metadata={'tag': 'self.counter3', 'display_name': 'test-server'},
    )
    resource_dict_2 = dict(
        resource_id='fake_resource_id2',
        project_id='fake_project_id',
        user_id="fake_user_id",
        timestamp='2012-07-02T10:42:00.000000',
        metadata={'tag': 'self.counter3', 'display_name': 'test-server'},
    )
    resource_1 = Resource(ResourceManager(None), resource_dict_1)
    resource_2 = Resource(ResourceManager(None), resource_dict_2)
    TEST.resources.add(resource_1)
    TEST.resources.add(resource_2)

    # samples
    sample_dict_1 = {'resource_id': 'fake_resource_id',
                   'project_id': 'fake_project_id',
                   'user_id': 'fake_user_id',
                   'counter_name': 'image',
                   'counter_type': 'gauge',
                   'counter_unit': 'image',
                   'counter_volume': 1,
                   'timestamp': '2012-12-21T11:00:55.000000',
                   'metadata': {'name1': 'value1', 'name2': 'value2'},
                    'message_id': 'fake_message_id'}
    sample_dict_2 = {'resource_id': 'fake_resource_id2',
                   'project_id': 'fake_project_id',
                   'user_id': 'fake_user_id',
                   'counter_name': 'image',
                   'counter_type': 'gauge',
                   'counter_unit': 'image',
                   'counter_volume': 1,
                   'timestamp': '2012-12-21T11:00:55.000000',
                   'metadata': {'name1': 'value1', 'name2': 'value2'},
                    'message_id': 'fake_message_id'}
    sample_1 = Sample(SampleManager(None), sample_dict_1)
    sample_2 = Sample(SampleManager(None), sample_dict_2)
    TEST.samples.add(sample_1)
    TEST.samples.add(sample_2)

    # meters
    meter_dict_1 = {'name': 'instance',
                  'type': 'gauge',
                  'unit': 'instance',
                  'resource_id': 'fake_resource_id',
                  'project_id': 'fake_project_id',
                  'user_id': 'fake_user_id'}
    meter_dict_2 = {'name': 'instance',
                  'type': 'gauge',
                  'unit': 'instance',
                  'resource_id': 'fake_resource_id',
                  'project_id': 'fake_project_id',
                  'user_id': 'fake_user_id'}
    meter_dict_3 = {'name': 'disk.read.bytes',
                  'type': 'gauge',
                  'unit': 'instance',
                  'resource_id': 'fake_resource_id',
                  'project_id': 'fake_project_id',
                  'user_id': 'fake_user_id'}
    meter_dict_4 = {'name': 'disk.write.bytes',
                  'type': 'gauge',
                  'unit': 'instance',
                  'resource_id': 'fake_resource_id',
                  'project_id': 'fake_project_id',
                  'user_id': 'fake_user_id'}
    meter_1 = Meter(MeterManager(None), meter_dict_1)
    meter_2 = Meter(MeterManager(None), meter_dict_2)
    meter_3 = Meter(MeterManager(None), meter_dict_3)
    meter_4 = Meter(MeterManager(None), meter_dict_4)
    TEST.meters.add(meter_1)
    TEST.meters.add(meter_2)
    TEST.meters.add(meter_3)
    TEST.meters.add(meter_4)

    # statistic
    statistic_dict_1 = {'min': 1,
                 'max': 9,
                 'avg': 4.55,
                 'sum': 45,
                 'count': 10,
                 'duration_start': '2012-12-21T11:00:55.000000',
                 'duration_end': '2012-12-21T11:00:55.000000',
                 'period': 7200,
                 'period_start': '2012-12-21T11:00:55.000000',
                 'period_end': '2012-12-21T11:00:55.000000'}
    statistic_1 = Statistics(StatisticsManager(None), statistic_dict_1)
    TEST.statistics.add(statistic_1)
