import logging
import urlparse

from django.conf import settings
from ceilometerclient import client as ceilometer_client
from horizon import exceptions
from openstack_dashboard.api.base import url_for

LOG = logging.getLogger(__name__)


def ceilometerclient(request):
    o = urlparse.urlparse(url_for(request, 'ceilometer'))
    url = "://".join((o.cheme, o.netloc))
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    LOG.debug('ceilometerclient connection created using token "%s" and url "%s"'
              % (request.user.token.id, url))
    return ceilometer_client('1', url, token=request.user.token.id,
                             insecure=insecure)


def sample_list(request, counter_name, resource_id, user_id, project_id, source):
    """List the samples for this meters."""
    try:
        samples = ceilometerclient(request).samples.list(counter_name=counter_name,
                                                         resource_id=resource_id, user_id=user_id, project_id=project_id)
    except:
        samples = []
        LOG.exceptions("Sapmles not found: %s" % counter_name)
        exceptions.handle(request)

    return samples


def meter_list(request, resource_id, user_id, project_id, source):
    """List the user's meters."""
    meters = ceilometerclient(request).meters.list(resource_id=resource_id,
                                                   user_id=user_id, project_id=project_id, source=source)
    return meters


def user_list(request):
    """List the users."""
    users = ceilometerclient(request).users.list()
    return users


def resource_list(request, source, user_id):
    """List the resources."""
    resources = ceilometerclient(request).\
        resources.list(source=source, user_id=user_id)
    return resources


def project_list(request, source):
    projects = ceilometerclient(request).projects.list(source=source)
    return projects
