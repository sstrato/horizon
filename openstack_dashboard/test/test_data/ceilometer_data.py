#from ceilometer.v1.meters import User, UserManager

from .utils import TestDataContainer


def data(TEST):
    #TEST.users = TestDataContainer()
    TEST.projects = TestDataContainer()
    TEST.resources = TestDataContainer()
    TEST.samples = TestDataContainer()
    TEST.meters = TestDataContainer()

    # users
    #user_dict = {}

    # projects
    project_dict = {'project_id': 'fake_project_id'}

    # resources
    resource_dict = {'resource_id': 'fake_resource_id',
                     'project_id': 'fake_project_id',
                     'user_id': "fake_user_id",
                     'received_timestamp': u'2013-01-11T12:59:37.582000',
                     'timestamp': u'2012-07-02T10:42:00.000000',
                     'metadata': {u'tag': u'self.counter3', u'display_name': u'test-server'},
                     'source': u'test_list_resources',
                     'meter':  [{u'counter_name': u'instance', u'counter_type': u'cumulative'}],
                     }
    # samples
    sample_dict = {'resource_id': 'fake_resource_id',
                   'counter_name': 'image',
                   'counter_type': 'gauge',
                   'counter_volume': 1,
                   'timestamp': '2012-12-21T11:00:55.000000'
                   }

    # meters
    meter_dict = {'resource_id': 'fake_resource_id',
                     'project_id': 'fake_project_id',
                     'user_id': None,
                     'counter_name': 'fake_counter_name',
                     'counter_type': 'fake_counter_type'}
