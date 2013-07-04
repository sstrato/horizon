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

from mox import IsA
from django import http

from openstack_dashboard import api
from openstack_dashboard.test import helpers as test


class CeilometerApiTests(test.APITestCase):
    def test_sample_list(self):
        samples = self.samples.list()
        meter_name = "meter_name"
        ceilometerclient = self.stub_ceilometerclient()
        ceilometerclient.samples = self.mox.CreateMockAnything()
        ceilometerclient.samples.list(meter_name=meter_name, q=[]).\
            AndReturn(samples)
        self.mox.ReplayAll()

        ret_list = api.ceilometer.sample_list(self.request,
                                              meter_name,
                                              query=[])
        for c in ret_list:
            self.assertIsInstance(c, api.ceilometer.Sample)

    def test_meter_list(self):
        meters = self.meters.list()
        ceilometerclient = self.stub_ceilometerclient()
        ceilometerclient.meters = self.mox.CreateMockAnything()
        ceilometerclient.meters.list(q=[]).AndReturn(meters)
        self.mox.ReplayAll()

        ret_list = api.ceilometer.meter_list(self.request, [])
        for m in ret_list:
            self.assertIsInstance(m, api.ceilometer.Meter)

    def test_reousrce_list(self):
        resources = self.resources.list()
        ceilometerclient = self.stub_ceilometerclient()
        ceilometerclient.resources = self.mox.CreateMockAnything()
        ceilometerclient.resources.list(q=[]).AndReturn(resources)
        self.mox.ReplayAll()

        ret_list = api.ceilometer.resource_list(self.request, query=[])
        for r in ret_list:
            self.assertIsInstance(r, api.ceilometer.Resource)

    def test_statistic_list(self):
        statistics = self.statistics.list()
        meter_name = "meter_name"
        ceilometerclient = self.stub_ceilometerclient()
        ceilometerclient.statistics = self.mox.CreateMockAnything()
        ceilometerclient.statistics.list(meter_name=meter_name, q=[]).\
            AndReturn(statistics)
        self.mox.ReplayAll()

        ret_list = api.ceilometer.statistic_list(self.request,
                                                 meter_name,
                                                 query=[])
        for s in ret_list:
            self.assertIsInstance(s, api.ceilometer.Statistic)

    @test.create_stubs({api.ceilometer: ("statistic_list",)})
    def test_global_usage_get(self):
        statistics = self.statistics.list()
        api.ceilometer.statistic_list(IsA(http.HttpRequest),
                                      IsA(str),
                                      query=IsA(list))\
                .MultipleTimes()\
                .AndReturn(statistics)
        self.mox.ReplayAll()

        meter_names = ["disk.read.bytes",
                       "disk.read.requests",
                       "disk.write.bytes",
                       "disk.write.requests"]
        usage = api.ceilometer.global_usage_get(self.request,
                                                meter_names,
                                                "user_1",
                                                "tenant_1",
                                                "resource_1")
        self.assertEqual(usage, {"user": "user_1",
                                 "tenant": "tenant_1",
                                 "resource": "resource_1",
                                 "disk.read.bytes": 9,
                                 "disk.write.bytes": 9,
                                 "disk.read.requests": 9,
                                 "disk.write.requests": 9})

    @test.create_stubs({api.ceilometer: ("statistic_list",)})
    def test_global_usage_get_without_data(self):
        api.ceilometer.statistic_list(IsA(http.HttpRequest),
                                      IsA(str),
                                      query=IsA(list))\
                .MultipleTimes()\
                .AndReturn([])
        self.mox.ReplayAll()

        meter_names = ["disk.read.bytes",
                       "disk.read.requests",
                       "disk.write.bytes",
                       "disk.write.requests"]
        usage = api.ceilometer.global_usage_get(self.request,
                                                meter_names,
                                                "user_1",
                                                "tenant_1",
                                                "resource_1")
        self.assertEqual(usage, {"user": "user_1",
                                 "tenant": "tenant_1",
                                 "resource": "resource_1",
                                 "disk.read.bytes": 0,
                                 "disk.write.bytes": 0,
                                 "disk.read.requests": 0,
                                 "disk.write.requests": 0})

    @test.create_stubs({api.ceilometer: ("global_usage_preload",)})
    def test_global_network_traffic_usage(self):
        usages = self.global_network_usages.list()
        fields = ["network.incoming.bytes", "network.incoming.packets",
                  "network.outgoing.bytes", "network.outgoing.packets"]
        api.ceilometer.global_usage_preload(IsA(http.HttpRequest), fields).\
            AndReturn(usages)
        self.mox.ReplayAll()
        usage_list = api.ceilometer.global_network_traffic_usage(self.request)
        for u in usage_list:
            self.assertIsInstance(u, api.ceilometer.GlobalNetworkTrafficUsage)

    @test.create_stubs({api.ceilometer: ("global_usage_preload",)})
    def test_global_disk_usage(self):
        usages = self.global_disk_usages.list()
        fields = ["network", "network_create",
                   "subnet", "subnet_create",
                   "port", "port_create",
                   "router", "router_create",
                   "ip_floating", "ip_floating_create"]
        api.ceilometer.global_usage_preload(IsA(http.HttpRequest), fields).\
            AndReturn(usages)
        self.mox.ReplayAll()
        usage_list = api.ceilometer.global_network_usage(self.request)
        for u in usage_list:
            self.assertIsInstance(u, api.ceilometer.GlobalNetworkUsage)

    @test.create_stubs({api.ceilometer: ("global_usage_preload",)})
    def test_global_network_usage(self):
        usages = self.global_network_usages.list()
        fields = ["disk.read.bytes", "disk.read.requests",
                  "disk.write.bytes", "disk.write.requests"]
        api.ceilometer.global_usage_preload(IsA(http.HttpRequest), fields).\
            AndReturn(usages)
        self.mox.ReplayAll()
        usage_list = api.ceilometer.global_disk_usage(self.request)
        for u in usage_list:
            self.assertIsInstance(u, api.ceilometer.GlobalDiskUsage)

    @test.create_stubs({api.ceilometer: ("global_usage_preload",)})
    def test_global_object_store_usage(self):
        usages = self.global_object_store_usages.list()
        fields = ["storage.objects",
                  "storage.objects.size",
                  "storage.objects.incoming.bytes",
                  "storage.objects.outgoing.bytes"]
        api.ceilometer.global_usage_preload(IsA(http.HttpRequest), fields).\
            AndReturn(usages)
        self.mox.ReplayAll()
        usage_list = api.ceilometer.global_object_store_usage(self.request)
        for u in usage_list:
            self.assertIsInstance(u, api.ceilometer.GlobalObjectStoreUsage)

    @test.create_stubs({api.ceilometer: ("meter_list",)})
    def test_global_usage_preload(self):
        meters = self.meters.list()
        fields = ["disk.read.bytes", "disk.read.requests",
                  "disk.write.bytes", "disk.write.requests"]
        api.ceilometer.meter_list(IsA(http.HttpRequest)).AndReturn(meters)
        self.mox.ReplayAll()

        preload_usages = api.ceilometer\
                .global_usage_preload(self.request, fields)
        self.assertEqual(preload_usages,
                         [{"tenant": "fake_project_id",
                           "user": "fake_user_id",
                           "resource": "fake_resource_id"}])
