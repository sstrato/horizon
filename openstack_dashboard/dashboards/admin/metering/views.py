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

from datetime import datetime
import itertools
import logging
import operator

from django.views.generic import TemplateView

from horizon import exceptions
from horizon import tabs
from openstack_dashboard.api import ceilometer

from .tabs import CeilometerOverviewTabs


LOG = logging.getLogger(__name__)


class IndexView(tabs.TabbedTableView):
    tab_group_class = CeilometerOverviewTabs
    template_name = 'admin/metering/index.html'


def to_hours(item):
    """
    Convert the time of a sample to hour level
    to strip the minute and second information.
    It's used to preprocess data before interpolation.
    """
    date_obj = datetime.strptime(item[0], '%Y-%m-%dT%H:%M:%S')
    new_date_str = date_obj.strftime("%Y-%m-%dT%H:00:00")
    return new_date_str, item[1]


def to_days(item):
    """
    Convert the time of a sample to day level
    to strip the hour, minute and second information.
    It's used to preprocess data before interpolation.
    """
    date_obj = datetime.strptime(item[0], '%Y-%m-%dT%H:%M:%S')
    new_date_str = date_obj.strftime("%Y-%m-%dT00:00:00")
    return new_date_str, item[1]


def reduce_metrics(samples):
    """
    Given a set of samples, group them by time and calculate the average
    value for that time point.
    """
    new_samples = []
    for key, items in itertools.groupby(samples, operator.itemgetter(0)):
        items = list(items)
        if len(items) > 0:
            avg = sum(map(lambda x: x[1], items)) / len(items)
        else:
            avg = 0
        new_samples.append([key, avg])
    return new_samples


class SamplesView(TemplateView):
    template_name = "admin/metering/samples.csv"

    def get(self, request, *args, **kwargs):
        meter = request.GET.get('meter', None)
        date_from = request.GET.get('from', None)
        date_to = request.GET.get('to', None)
        resource = request.GET.get('resource', None)

        if not(meter and date_from and date_to and resource):
            raise exceptions.NotFound
        else:
            date_from += "T00:00:00"
            date_to += "T23:59:59"
            try:
                date_from_obj = datetime.strptime(date_from,
                                        "%Y-%m-%dT%H:%M:%S")
                date_to_obj = datetime.strptime(date_to, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise exceptions.NotFound

            query = [{'field': 'timestamp',
                      'op': 'ge',
                      'value': date_from},
                     {'field': 'timestamp',
                      'op': 'le',
                      'value': date_to},
                     {'field': 'resource',
                      'op': 'eq',
                      'value': resource}]
            sample_list = ceilometer.sample_list(self.request, meter, query)
            samples = []
            for sample_data in sample_list:
                samples.append([sample_data.timestamp[:19],
                                sample_data.counter_volume])

            # if requested period is too long interpolate data
            delta = (date_to_obj - date_from_obj).days

            if delta >= 365:
                samples = map(to_days, samples)
                samples = reduce_metrics(samples)
            elif delta >= 30:
                # reduce metrics to hours
                samples = map(to_hours, samples)
                samples = reduce_metrics(samples)

            context = dict(samples=samples)
            response_kwargs = dict(mimetype='text/csv')
            return self.render_to_response(
                    context=context,
                    **response_kwargs)
