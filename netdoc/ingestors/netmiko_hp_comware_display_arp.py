__author__     = 'Andrea Dainese'
__contact__    = 'andrea@adainese.it'
__copyright__  = 'Copyright 2022, Andrea Dainese'
__license__    = 'GPLv3'
__date__       = '2022-09-19'
__version__    = '0.9.8'

from os.path import basename
import logging
import inspect
from slugify import slugify
from . import functions

def ingest(log, force=False):
    """
    Processing display arp
    """
    function_name = ''.join(basename(__file__).split('.')[0])
    if function_name != functions.parsing_function_from_log(log):
        raise functions.WrongParser(f'Cannot use {function_name} for log {log.pk}')
    if not log.parsed:
        raise functions.NotParsed(f'Skipping unparsed log {log.pk}')
    if not log.parsed_output:
        raise functions.NotParsed(f'Skipping empty parsed log {log.pk}')
    if not force and log.ingested:
        raise functions.AlreadyIngested(f'Skipping injested log {log.pk}')
    if not log.discoverable.device:
        raise functions.Postponed(f'Device is required, postponing {log.pk}')

    for item in log.parsed_output:
        # Parsing
        # https://github.com/networktocode/ntc-templates/blob/master/tests/hp_comware/display_arp/hp_comware_display_arp.yml
        site_o = log.discoverable.device.site
        device_o = log.discoverable.device
        ip_address = item['ipaddress']
        mac_address = item['macaddress']
        interface_name = item['interface']

        interface_o = functions.set_get_interface(label=interface_name, device=device_o, create_kwargs={'name': interface_name})
        arpentry_o = functions.set_get_arpentry(interface=interface_o, ip_address=ip_address, mac_address=mac_address)


    # Update the log
    log.discoverable.save()
    log.ingested = True
    log.save()
