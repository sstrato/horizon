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

from django import http
from mox import IsA

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
        ceilometerclient.meters.list([]).AndReturn(meters)
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

    @test.create_stubs({api.ceilometer: ("statistic_list",),
                        api.ceilometer.CachedResources: ("get_user_name",
                                                         "get_tenant_name")})
    def test_global_usage_get(self):
        statistics = self.statistics.list()
        api.ceilometer.statistic_list(IsA(http.HttpRequest),
                                      IsA(str),
                                      query=IsA(list))\
                .MultipleTimes()\
                .AndReturn(statistics)
        api.ceilometer.CachedResources\
                .get_user_name(IsA(http.HttpRequest),
                               IsA(str)).AndReturn("user")
        api.ceilometer.CachedResources\
                .get_tenant_name(IsA(http.HttpRequest),
                                 IsA(str)).AndReturn("tenant")

        self.mox.ReplayAll()

        meter_names = ["disk.read.bytes",
                       "disk.read.requests",
                       "disk.write.bytes",
                       "disk.write.requests"]
        usage = api.ceilometer.global_usage_get(self.request,
                                                meter_names,
                                                "tenant__user__resource",
                                                )
        self.assertEqual(usage, {
            "id": "tenant__user__resource",
            "user": "user",
            "tenant": "tenant",
            "resource": "resource",
            "disk_read_bytes": 9,
            "disk_write_bytes": 9,
            "disk_read_requests": 9,
            "disk_write_requests": 9})

    @test.create_stubs({api.ceilometer: ("statistic_list",),
                        api.ceilometer.CachedResources: ("get_user_name",
                                                         "get_tenant_name")})
    def test_global_usage_get_without_data(self):
        api.ceilometer.statistic_list(IsA(http.HttpRequest),
                                      IsA(str),
                                      query=IsA(list))\
                .MultipleTimes()\
                .AndReturn([])

        api.ceilometer.CachedResources\
                .get_user_name(IsA(http.HttpRequest),
                               IsA(str)).AndReturn("user")
        api.ceilometer.CachedResources\
                .get_tenant_name(IsA(http.HttpRequest),
                                 IsA(str)).AndReturn("tenant")

        self.mox.ReplayAll()

        meter_names = ["disk.read.bytes",
                       "disk.read.requests",
                       "disk.write.bytes",
                       "disk.write.requests"]
        usage = api.ceilometer.global_usage_get(self.request,
                                                meter_names,
                                                "tenant__user__resource",)
        self.assertEqual(usage, {
            "id": "tenant__user__resource",
            "user": "user",
            "tenant": "tenant",
            "resource": "resource",
            "disk_read_bytes": 0,
            "disk_write_bytes": 0,
            "disk_read_requests": 0,
            "disk_write_requests": 0})

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

    @test.create_stubs({api.ceilometer.CachedResources: ("get_meter_list",
                                                         "get_user_name",
                                                         "get_tenant_name")})
    def test_global_usage_preload(self):
        meters = self.meters.list()
        fields = ["disk.read.bytes", "disk.read.requests",
                  "disk.write.bytes", "disk.write.requests"]
        api.ceilometer.CachedResources\
                .get_meter_list(IsA(http.HttpRequest))\
                .AndReturn(meters)
        api.ceilometer.CachedResources\
                .get_user_name(IsA(http.HttpRequest),
                               IsA(str))\
                .MultipleTimes()\
                .AndReturn("user")
        api.ceilometer.CachedResources\
                .get_tenant_name(IsA(http.HttpRequest),
                                 IsA(str))\
                .MultipleTimes()\
                .AndReturn("tenant")

        self.mox.ReplayAll()

        preload_usages = api.ceilometer\
                .global_usage_preload(self.request, fields)
        self.assertEqual(preload_usages,
                     [{"id": "fake_project_id__fake_user_id__fake_resource_id",
                       "tenant": "tenant",
                       "user": "user",
                       "resource": "fake_resource_id"}])
