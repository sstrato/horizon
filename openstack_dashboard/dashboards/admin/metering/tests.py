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
from django.core.urlresolvers import reverse

from mox import IsA

from openstack_dashboard import api
from openstack_dashboard.test import helpers as test


INDEX_URL = reverse("horizon:admin:metering:index")


class MeteringViewTests(test.BaseAdminViewTests):
    @test.create_stubs({api.ceilometer: ("global_disk_usage",
                                     "global_network_traffic_usage",
                                     "global_network_usage",
                                     "global_object_store_usage",
                                         "meter_list")})
    def test_index(self):
        global_disk_usages = self.global_disk_usages.list()
        global_network_usages = self.global_network_usages.list()
        global_network_traffic_usages = self.global_network_traffic_usages\
                                            .list()
        global_object_store_usages = self.global_object_store_usages.list()
        meters = self.meters.list()

        api.ceilometer.global_disk_usage(IsA(http.HttpRequest))\
            .AndReturn(global_disk_usages)
        api.ceilometer.global_network_usage(IsA(http.HttpRequest))\
            .AndReturn(global_network_usages)
        api.ceilometer.global_network_traffic_usage(IsA(http.HttpRequest))\
            .AndReturn(global_network_traffic_usages)
        api.ceilometer.global_object_store_usage(IsA(http.HttpRequest))\
            .AndReturn(global_object_store_usages)
        api.ceilometer.meter_list(IsA(http.HttpRequest)).AndReturn(meters)
        self.mox.ReplayAll()

        res = self.client.get(INDEX_URL)
        self.assertTemplateUsed(res, "admin/metering/index.html")
