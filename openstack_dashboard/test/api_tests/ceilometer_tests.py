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

        ret_list = api.ceilometer.meter_list(self.request, query=[])
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

    @test.create_stubs({api.ceilometer: ("global_usage",)})
    def test_global_network_traffic_usage(self):
        usages = self.global_network_usages.list()
        fields = ["network.incoming.bytes", "network.incoming.packets",
                  "network.outgoing.bytes", "network.outgoing.packets"]
        api.ceilometer.global_usage(IsA(http.HttpRequest), fields).\
            AndReturn(usages)
        self.mox.ReplayAll()
        usage_list = api.ceilometer.global_network_traffic_usage(self.request)
        for u in usage_list:
            self.assertIsInstance(u, api.ceilometer.GlobalNetworkTrafficUsage)

    @test.create_stubs({api.ceilometer: ("global_usage",)})
    def test_global_disk_usage(self):
        usages = self.global_disk_usages.list()
        fields = ["disk.read.bytes", "disk.read.requests",
                  "disk.write.bytes", "disk.write.requests"]
        api.ceilometer.global_usage(IsA(http.HttpRequest), fields).\
            AndReturn(usages)
        self.mox.ReplayAll()
        usage_list = api.ceilometer.global_disk_usage(self.request)
        for u in usage_list:
            self.assertIsInstance(u, api.ceilometer.GlobalDiskUsage)

    def test__group_usage(self):
        usage_list = [{"tenant": "tenant1",
                     "user": "user1",
                     "total": 10,
                     "counter_name": "disk_read_bytes",
                     "resource": "resource1"},
                     {"tenant": "tenant1",
                     "user": "user1",
                     "total": 10,
                     "counter_name": "disk_read_requests",
                     "resource": "resource1"},
                     {"tenant": "tenant1",
                     "user": "user1",
                     "total": 10,
                     "counter_name": "disk_write_bytes",
                     "resource": "resource1"},
                     {"tenant": "tenant1",
                     "user": "user1",
                     "total": 10,
                     "counter_name": "disk_write_requests",
                     "resource": "resource1"}]
        ret_list = api.ceilometer._group_usage(usage_list)
        for r in ret_list:
            self.assertEquals(r['tenant'], "tenant1")
            self.assertEquals(r['user'], "user1")
            self.assertEquals(r['disk_read_requests'], 10)
            self.assertEquals(r['disk_read_bytes'], 10)
            self.assertEquals(r['disk_write_bytes'], 10)
            self.assertEquals(r['disk_write_requests'], 10)
            self.assertEquals(r['resource'], 'resource1')

    @test.create_stubs({api.keystone: ("user_list", "tenant_list",),
                        api.ceilometer: ("meter_list", "statistic_list")})
    def test_global_usage(self):
        users = self.users.list()
        tenants = self.tenants.list()
        meters = [api.ceilometer.Meter(m) for m in self.meters.list()]
        statistics = [api.ceilometer.Statistic(s) for
                      s in self.statistics.list()]
        fields = ["disk.read.bytes", "disk.read.requests",
                  "disk.write.bytes", "disk.write.requests"]

        api.keystone.user_list(IsA(http.HttpRequest)).AndReturn(users)
        api.keystone.tenant_list(IsA(http.HttpRequest))\
            .AndReturn((tenants, False))
        api.ceilometer.meter_list(IsA(http.HttpRequest)).AndReturn(meters)
        api.ceilometer.statistic_list(IsA(http.HttpRequest),
            IsA(str), query=IsA(list)).MultipleTimes("1").AndReturn(statistics)
        self.mox.ReplayAll()

        api.ceilometer.global_usage(self.request, fields)
