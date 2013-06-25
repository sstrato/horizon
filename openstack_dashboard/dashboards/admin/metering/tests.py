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

from django.core.urlresolvers import reverse
from django import http
from mox import IsA

from openstack_dashboard import api
from openstack_dashboard.test import helpers as test

from .views import to_days
from .views import to_hours
from .views import reduce_metrics


INDEX_URL = reverse("horizon:admin:metering:index")


class MeteringViewTests(test.BaseAdminViewTests):
    @test.create_stubs({api.ceilometer: ("global_disk_usage",
                                         "global_network_traffic_usage",
                                         "global_network_usage",
                                         "global_object_store_usage",
                                         "meter_list")})
    def test_index_view(self):
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

    @test.create_stubs({api.ceilometer: ("sample_list",)})
    def test_sample_views(self):
        samples = self.samples.list()
        api.ceilometer.sample_list(IsA(http.HttpRequest), IsA(basestring),
                                   IsA(list)).AndReturn(samples)
        self.mox.ReplayAll()

        res = self.client.get(reverse("horizon:admin:metering:samples") +
                        '?meter=meter&from=2012-10-10&'
                        'to=2012-10-11&resource=resouce')
        self.assertTemplateUsed(res, "admin/metering/samples.csv")

    def test_sample_views_without_request_args(self):
        res = self.client.get(reverse("horizon:admin:metering:samples"))
        self.assertEqual(res.status_code, 404)

    def test_sample_views_wrong_dates(self):
        res = self.client.get(reverse("horizon:admin:metering:samples"),
                              dict(meter="meter",
                                   date_from="cannot be parsed",
                                   date_to="cannot be parsed",
                                   resource="resource")
                              )
        self.assertEqual(res.status_code, 404)

    def test_to_days_to_hours(self):
        test_data = (["2001-01-01T01:01:01", 123],
                     ["1999-12-12T00:00:00", 321],
                     ["9999-12-12T12:59:59", 0])
        for test in test_data:
            date, value = to_days(test)
            self.assertEqual(date, test[0][:11] + "00:00:00")
            self.assertEqual(value, test[1])
        for test in test_data:
            date, value = to_hours(test)
            self.assertEqual(date, test[0][:14] + "00:00")
            self.assertEqual(value, test[1])

    def test_reduce_metrics(self):
        test_data = [["2001-01-01T00:00:00", 123],
                     ["2001-01-01T00:00:00", 321],
                     ["2001-01-01T00:00:00", 0],
                     ["2001-01-02T00:00:00", 2],
                     ["2001-01-02T00:00:00", 2],
                     ["2001-01-02T00:00:00", 2]]
        result = reduce_metrics(test_data)
        self.assertEqual(result, [["2001-01-01T00:00:00", 444 / 3],
                                  ["2001-01-02T00:00:00", 6 / 3]])
