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
from django.db.utils import IntegrityError
from . import functions

def ingest(log, force=False):
    """
    Processing hostname.
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

    item = log.parsed_output[0] # Show version contains only one item

    # Parsing
    name = item["hostname"]
    manufacturer = 'Linux'
    site = log.discoverable.site
    create_argws = {
        'site': site,
        'manufacturer': manufacturer,
    }

    # Trusted data: we always update some data
    device_o = functions.set_get_device(name=name, create_kwargs=create_argws)
    discoverable_o = functions.set_get_discoverable(address=log.discoverable.address, device=device_o, site=site, force=True)

    # Update the log
    log.ingested = True
    log.save()
