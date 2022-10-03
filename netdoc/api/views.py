__author__     = 'Andrea Dainese'
__contact__    = 'andrea@adainese.it'
__copyright__  = 'Copyright 2022, Andrea Dainese'
__license__    = 'GPLv3'
__date__       = '2022-09-07'
__version__    = '0.9.8'

from django.db.models import Count

from netbox.api.viewsets import NetBoxModelViewSet

from .. import models
from .serializers import CredentialSerializer, DiscoverableSerializer, DiscoveryLogSerializer


class CredentialViewSet(NetBoxModelViewSet):
    queryset = models.Credential.objects.prefetch_related('tags').annotate(
        discoverables_count=Count('discoverables')
    )
    serializer_class = CredentialSerializer  


class DiscoverableViewSet(NetBoxModelViewSet):
    queryset = models.Discoverable.objects.prefetch_related('credential', 'tags').annotate(
        discoverylogs_count=Count('discoverylogs')
    )
    serializer_class = DiscoverableSerializer
    # filterset_class = filtersets.AccessListRuleFilterSet


class DiscoveryLogViewSet(NetBoxModelViewSet):
    queryset = models.DiscoveryLog.objects.prefetch_related('discoverable', 'tags')
    serializer_class = DiscoveryLogSerializer
    # filterset_class = filtersets.AccessListRuleFilterSet  
