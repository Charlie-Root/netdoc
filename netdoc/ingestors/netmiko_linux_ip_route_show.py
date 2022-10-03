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
    Processing ip route show.
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
        vrf_name = log.command.split(" table ").pop() # The vrf is embedded in the command
        device_o = log.discoverable.device
        interface_name = item['nexthop_if']
        if item['network'].startswith('default'):
            destination = '0.0.0.0/0'
        elif '/' in item['network']:
            destination = item['network']
        else:
            destination = f"{item['network']}/32"

        args = {
            'device': device_o,
            'distance': item['metric'],
            'destination': destination,
            'metric': item['metric'],
            'type': item['protocol'],
        }

        if item['nexthop_if']:
            args['nexthop_if'] = functions.set_get_interface(label=interface_name, device=device_o, create_kwargs={'name': interface_name})
        if item['nexthop_ip']:
            args['nexthop_ip'] = item['nexthop_ip']
        if vrf_name:
            vrf_o = functions.set_get_vrf(name=vrf_name, create_kwargs={})
            args['vrf'] = vrf_o
        
        route_o = functions.set_get_route(**args)

    # Update the log
    log.discoverable.save()
    log.ingested = True
    log.save()
