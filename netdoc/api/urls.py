__author__     = 'Andrea Dainese'
__contact__    = 'andrea@adainese.it'
__copyright__  = 'Copyright 2022, Andrea Dainese'
__license__    = 'GPLv3'
__date__       = '2022-09-07'
__version__    = '0.9.8'

from netbox.api.routers import NetBoxRouter
from . import views


app_name = 'nedoc'

router = NetBoxRouter()
router.register('credentials', views.CredentialViewSet)
router.register('discoverables', views.DiscoverableViewSet)
router.register('discoverylogs', views.DiscoveryLogViewSet)

urlpatterns = router.urls
