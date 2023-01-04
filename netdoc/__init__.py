__author__     = 'Andrea Dainese'
__contact__    = 'andrea@adainese.it'
__copyright__  = 'Copyright 2022, Andrea Dainese'
__license__    = 'GPLv3'
__date__       = '2022-09-07'
__version__    = '0.9.8'

from extras.plugins import PluginConfig
from django.conf import settings
import os

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get('netdoc', {})

class NetdocConfig(PluginConfig):
    name = 'netdoc'
    verbose_name = 'NetDoc'
    description = 'Automatic Network Documentation plugin for NetBox'
    version = __version__
    author = 'Andrea Dainese'
    author_email = 'andrea@adainese.it'
    base_url = 'netdoc'
    required_settings = ['NTC_TEMPLATES_DIR']
    default_settings = {
        'NTC_TEMPLATES_DIR': '/opt/ntc-templates/ntc_templates/templates'
    }


config = NetdocConfig

# Setting NTC_TEMPLATES_DIR
os.environ.setdefault("NET_TEXTFSM", PLUGIN_SETTINGS.get('NTC_TEMPLATES_DIR'))
