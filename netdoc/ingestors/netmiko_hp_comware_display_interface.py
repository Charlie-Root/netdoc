__author__     = 'Andrea Dainese'
__contact__    = 'andrea@adainese.it'
__copyright__  = 'Copyright 2022, Andrea Dainese'
__license__    = 'GPLv3'
__date__       = '2022-09-07'
__version__    = '0.9.8'

from os.path import basename
import logging
import inspect
from slugify import slugify
from . import functions

def ingest(log, force=False):
    """
    Processing show interfaces.
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
        # https://github.com/dainok/ntc-templates/blob/hpe-templates/tests/hp_comware/display_interface/hp_comware_display_interface.yml
        device_o = log.discoverable.device
        interface_name = item['intf']
        trunking_vlans=functions.normalize_trunking_vlans(item["vlan_passing"])
        args = {
            'description': item['description'],
            'duplex': functions.normalize_interface_duplex(item['duplex']),
            'speed': functions.normalize_interface_bandwidth(item['bandwidth']),
            'name': interface_name,
            'mac_address': item['hw_address'].pop() if item['hw_address'] else None,
            'mode': functions.normalize_switchport_mode(item['port_link_type']),
        }

        try:
            args['mtu'] = int(item['mtu'])
        except ValueError:
            pass

        # interface_parent = functions.parent_interface(interface_name)
        # if interface_parent:
        #     args['parent'] = functions.set_get_interface(label=interface_parent, device=device_o)

        # Trusted data: we always update some data
        interface_o = functions.set_get_interface(label=interface_name, device=device_o, create_kwargs=args, update_kwargs=args)
 
        if force:
            # Clear all associated IP addresses
            interface_o.tagged_vlans.clear()

        if args['mode'] == 'tagged':
            # Add native VLAN
            args['untagged_vlan'] = functions.set_get_vlan(vid=item['vlan_native'], site=site_o)
            # Add VLANs to the interface
            for vid in trunking_vlans:
                vlan_o = functions.set_get_vlan(vid=vid, site=site_o)
                try:
                    # VLAN already present
                    interface_o.tagged_vlans.get(pk=vlan_o.pk)
                except:
                    # Adding VLAN
                    interface_o.tagged_vlans.add(vlan_o)
            interface_o.save()

    # Update the log
    log.ingested = True
    log.save()
