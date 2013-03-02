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
from django.utils.translation import ugettext_lazy as _

from horizon import tabs
from openstack_dashboard.api import ceilometer

from .tables import GlobalDiskUsageTable
from .tables import GlobalNetworkTrafficUsageTable
from .tables import GlobalNetworkUsageTable
from .tables import GlobalObjectStoreUsageTable


class GlobalDiskUsageTab(tabs.TableTab):
    table_classes = (GlobalDiskUsageTable,)
    name = _("Global Disk Usage")
    slug = "global_disk_usage"
    template_name = ("horizon/common/_detail_table.html")

    def get_global_disk_usage_data(self):
        request = self.tab_group.request
        result = ceilometer.global_disk_usage(request)
        return result


class GlobalNetworkTrafficUsageTab(tabs.TableTab):
    table_classes = (GlobalNetworkTrafficUsageTable,)
    name = _("Global Network Traffic Usage")
    slug = "global_network_traffic_usage"
    template_name = ("horizon/common/_detail_table.html")

    def get_global_network_traffic_usage_data(self):
        request = self.tab_group.request
        result = ceilometer.global_network_traffic_usage(request)
        return result


class GlobalNetworkUsageTab(tabs.TableTab):
    table_classes = (GlobalNetworkUsageTable,)
    name = _("Global Network Usage")
    slug = "global_network_usage"
    template_name = ("horizon/common/_detail_table.html")

    def get_global_network_usage_data(self):
        request = self.tab_group.request
        result = ceilometer.global_network_usage(request)
        return result

    def allowed(self, request):
        permissions = ("openstack.services.network",)
        return request.user.has_perms(permissions)


class GlobalObjectStoreUsageTab(tabs.TableTab):
    table_classes = (GlobalObjectStoreUsageTable,)
    name = _("Global Object Store Usage")
    slug = "global_object_store_usage"
    template_name = ("horizon/common/_detail_table.html")

    def get_global_object_store_usage_data(self):
        request = self.tab_group.request
        result = ceilometer.global_object_store_usage(request)
        return result

    def allowed(self, request):
        permissions = ("openstack.services.object-store",)
        return request.user.has_perms(permissions)


class GlobalStatsTab(tabs.Tab):
    name = _("Stats")
    slug = "stats"
    template_name = ("admin/metering/stats.html")

    def get_context_data(self, request):
        meters = ceilometer.CachedResources.get_meter_list(request)
        # Now only 'cpu_utl' data is useful for line chart.
        meters = filter(lambda m: m.name == "cpu_util", meters)
        context = {'meters': meters}
        return context


class CeilometerOverviewTabs(tabs.TabGroup):
    slug = "ceilometer_overview"
    tabs = (GlobalDiskUsageTab, GlobalNetworkTrafficUsageTab,
            GlobalNetworkUsageTab, GlobalObjectStoreUsageTab, GlobalStatsTab,)
    sticky = True
