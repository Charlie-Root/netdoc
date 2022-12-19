__author__     = 'Andrea Dainese'
__contact__    = 'andrea@adainese.it'
__copyright__  = 'Copyright 2022, Andrea Dainese'
__license__    = 'GPLv3'
__date__       = '2022-09-13'
__version__    = '0.9.8'

import os
import logging
import django_rq
import pprint
from django.conf import settings

from nornir.core.plugins.inventory import InventoryPluginRegister
from .nornir_inventory import AssetInventory
from nornir import InitNornir
from nornir.core.filter import F
from . import discovery_linux, discovery_cisco_ios, discovery_cisco_nxos, discovery_cisco_xr

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get('netdoc', {})

def discovery(addresses):
    ntc_template_dir = os.environ.get("NET_TEXTFSM")
    if not ntc_template_dir:
        logging.error("NET_TEXTFSM not set in configuration.py")
        raise Exception("NET_TEXTFSM not set")
    elif not os.path.exists(ntc_template_dir):
        logging.error(f"{ntc_template_dir} not found")
        raise Exception("NET_TEXTFSM not found")

    # Configuring Nornir
    logger = logging.getLogger("nornir")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(PLUGIN_SETTINGS.get('NORNIR_LOG'))
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    # Load Nornir custom inventory
    InventoryPluginRegister.register("asset-inventory", AssetInventory)

    # Create Nornir inventory
    nr = InitNornir(
        runner={
            "plugin": "threaded",
            "options": {
                "num_workers": 100,
            },
        },
        inventory={"plugin": "asset-inventory"},
        logging={"enabled": False},
    )

    # Execute on a selected hosts only
    # See https://theworldsgonemad.net/2021/nornir-inventory/
    nr = nr.filter(F(hostname__in=addresses))

    # Starting discovery job
    pprint.pprint(nr.dict())
    discovery_linux.discovery(nr)
    discovery_cisco_ios.discovery(nr)
    discovery_cisco_nxos.discovery(nr)
    discovery_cisco_xr.discovery(nr)
