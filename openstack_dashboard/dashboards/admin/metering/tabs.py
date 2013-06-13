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
import operator

from django.utils.translation import ugettext_lazy as _
from django.core.context_processors import csrf

from horizon import tabs
from openstack_dashboard.api import ceilometer

from .tables import (DiskUsageTable, NetworkTrafficUsageTable,
                     ObjectStoreUsageTable, NetworkUsageTable)


class DiskUsageTab(tabs.TableTab):
    table_classes = (DiskUsageTable,)
    name = _("Global Disk Usage")
    slug = "global_disk_usage"
    template_name = ("horizon/common/_detail_table.html")

    def get_global_disk_usage_data(self):
        request = self.tab_group.request
        result = sorted(ceilometer.global_disk_usage(request),
                        key=operator.itemgetter('tenant', 'user'))
        return result


class NetworkTrafficUsageTab(tabs.TableTab):
    table_classes = (NetworkTrafficUsageTable,)
    name = _("Global Network Traffic Usage")
    slug = "global_network_traffic_usage"
    template_name = ("horizon/common/_detail_table.html")

    def get_global_network_traffic_usage_data(self):
        request = self.tab_group.request
        result = sorted(ceilometer.global_network_traffic_usage(request),
                        key=operator.itemgetter('tenant', 'user'))
        return result


class NetworkUsageTab(tabs.TableTab):
    table_classes = (NetworkUsageTable,)
    name = _("Global Network Usage")
    slug = "global_network_usage"
    template_name = ("horizon/common/_detail_table.html")

    def get_global_network_usage_data(self):
        request = self.tab_group.request
        result = sorted(ceilometer.global_network_usage(request),
                        key=operator.itemgetter('tenant', 'user'))
        return result

    def allowed(self, request):
        permissions = ("openstack.services.network",)
        return request.user.has_perms(permissions)


class GlobalObjectStoreUsageTab(tabs.TableTab):
    table_classes = (ObjectStoreUsageTable,)
    name = _("Global Object Store Usage")
    slug = "global_object_store_usage"
    template_name = ("horizon/common/_detail_table.html")

    def get_global_object_store_usage_data(self):
        request = self.tab_group.request
        result = sorted(ceilometer.global_object_store_usage(request),
                        key=operator.itemgetter('tenant', 'user'))
        return result

    def allowed(self, request):
        permissions = ("openstack.services.object-store",)
        return request.user.has_perms(permissions)


class StatsTab(tabs.Tab):
    name = _("Stats")
    slug = "stats"
    template_name = ("admin/metering/stats.html")

    def get_context_data(self, request):
        meters = ceilometer.meter_list(self.request)
        # Remove gauge type data.
        meters = filter(lambda m: m.type == "cumulative", meters)

        # Remove meters with the same name.
        cached_meter_names = []
        cached_meters = []
        for m in meters:
            if m.name not in cached_meter_names:
                cached_meter_names.append(m.name)
                cached_meters.append(m)

        context = {
            'meters': meters,
            'meters_unique_names': cached_meters,
        }
        context.update(csrf(request))
        return context


class CeilometerOverviewTabs(tabs.TabGroup):
    slug = "ceilometer_overview"
    tabs = (DiskUsageTab, NetworkTrafficUsageTab, NetworkUsageTab,
            GlobalObjectStoreUsageTab, StatsTab,)
    sticky = True
