__author__     = 'Andrea Dainese'
__contact__    = 'andrea@adainese.it'
__copyright__  = 'Copyright 2022, Andrea Dainese'
__license__    = 'GPLv3'
__date__       = '2022-09-19'
__version__    = '0.9.6'

from os.path import basename
import logging
import inspect
from slugify import slugify
from . import functions

def ingest(log, force=False):
    """
    Processing ip link show.
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

    site_o = log.discoverable.site

    for item in log.parsed_output:
        # Parsing
        device_o = log.discoverable.device
        interface_name = item['interface']
        args = {
            'name': interface_name,
            'mac_address': item['address'],
        }

        try:
            args['mtu'] = int(item['mtu'])
        except ValueError:
            pass

        if item['master']:
            args['parent'] = functions.set_get_interface(label=item['master'], device=device_o)

        # Trusted data: we always update some data
        interface_o = functions.set_get_interface(label=interface_name, device=device_o, create_kwargs=args, update_kwargs=args)
 
    # Update the log
    log.ingested = True
    log.save()
