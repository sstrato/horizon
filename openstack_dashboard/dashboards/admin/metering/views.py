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
import csv
from datetime import datetime, timedelta

from horizon import tabs
from django.http import HttpResponse
from django.views.generic import View

from .tabs import CeilometerOverviewTabs
from openstack_dashboard.api import ceilometer

import itertools
import operator

LOG = logging.getLogger(__name__)


class IndexView(tabs.TabbedTableView):
    tab_group_class = CeilometerOverviewTabs
    template_name = 'admin/metering/index.html'


# convert all items in list to hour level
def to_hours(item):
    date_obj = datetime.strptime(item[0], '%Y-%m-%dT%H:%M:%S')
    new_date_str = date_obj.strftime("%Y-%m-%dT%H:00:00")
    return new_date_str, item[1]


# convert all items in list to day level
def to_days(item):
    date_obj = datetime.strptime(item[0], '%Y-%m-%dT%H:%M:%S')
    new_date_str = date_obj.strftime("%Y-%m-%dT00:00:00")
    return new_date_str, item[1]


# given a set of metrics with same key, group them and calc average
def reduce_metrics(samples):
    new_samples = []
    for key, items in itertools.groupby(samples, operator.itemgetter(0)):
        grouped_items = []
        for item in items:
            grouped_items.append(item[1])
        item_len = len(grouped_items)
        if item_len > 0:
            avg = reduce(lambda x, y: x + y, grouped_items) / item_len
        else:
            avg = 0

        new_samples.append([key, avg])
    return new_samples


class SamplesView(View):
    def get(self, request, *args, **kwargs):
        source = request.GET.get('sample', None)
        date_from = request.GET.get('from', None)
        date_to = request.GET.get('to', None)
        resource = request.GET.get('resource', None)
        query = []

        if date_from:
            date_from += " 00:00:00"
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
            # Get the data ahead of the date_from timestamp.
            # Cumulative data like cpu is always increasing which
            # means that the later one should minus the previous one to
            # get correct delta value.
            # The timedelta is the interval for ceilometer to collect data.
            previous_time_obj = date_from_obj - timedelta(minutes=10)
            query.append({'field': 'timestamp', 'op': 'ge',
                          'value': previous_time_obj})

        if date_to:
            date_to += " 23:59:59"
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
            query.append({'field': 'timestamp', 'op': 'le', 'value': date_to})

        samples = []
        if source and resource:
            query.append({'field': 'resource', 'op': 'eq', 'value': resource})
            sample_list = ceilometer.sample_list(self.request, source, query)
            previous = 0
            if sample_list:
                first_time_obj = datetime.strptime(sample_list[0].timestamp[:19], '%Y-%m-%dT%H:%M:%S')
                if first_time_obj >= date_from_obj:
                    # No data exists ahead of the from timestamp.
                    previous = 0
                else:
                    # The first data is a previous one not in the query period.
                    previous = sample_list[0].counter_volume
                    sample_list.pop(0)

            for sample_data in sample_list:
                current_volume = sample_data.counter_volume
                current_delta = current_volume - previous
                previous = current_volume
                if current_delta < 0:
                    current_delta = current_volume
                samples.append([sample_data.timestamp[:19], current_delta])

        # if requested period is too long interpolate data
        delta = (date_to_obj - date_from_obj).days

        if delta >= 365:
            samples = map(to_days, samples)
            samples = reduce_metrics(samples)
        elif delta >= 30:
            # reduce metrics to hours
            samples = map(to_hours, samples)
            samples = reduce_metrics(samples)

        # output csv
        headers = ['date', 'value']
        response = HttpResponse(mimetype='text/csv')
        writer = csv.writer(response)
        writer.writerow(headers)

        for sample in samples:
            writer.writerow(sample)

        return response
