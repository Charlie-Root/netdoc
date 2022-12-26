__author__     = 'Andrea Dainese'
__contact__    = 'andrea@adainese.it'
__copyright__  = 'Copyright 2022, Andrea Dainese'
__license__    = 'GPLv3'
__date__       = '2022-09-19'
__version__    = '0.9.8'

import json
from ctypes import addressof
from django.utils import timezone
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
from nornir.core.filter import F
from . import models
from . import functions

def discovery(nr):
    """
    Discovery HP Comware devices
    """
    mode = "netmiko"
    platform = "hp_comnware"
    filtered_devices = nr.filter(platform=platform)
    enable=True
    logs = []

    # Define tasks
    def multiple_tasks(task):
        """
        Define tasks for the playbook. CMD line is passed also as name, so we
        can log cmdline, stdout (result) and parsed output.
        """
        task.run(
            task=netmiko_send_command,
            name="display current-configuration",
            command_string="display current-configuration",
            use_textfsm=False,
            enable=enable,
        )
        task.run(task=netmiko_send_command, name="display version", command_string="display version", use_textfsm=False, enable=enable)
        task.run(task=netmiko_send_command, name="display logbuffer level 6", command_string="display logbuffer level 6", use_textfsm=False, enable=enable)
        task.run(
            task=netmiko_send_command, name="display interface", command_string="display interface", use_textfsm=False, enable=enable
        )
        task.run(
            task=netmiko_send_command,
            name="display lldp neighbor-information verbose",
            command_string="display lldp neighbor-information verbose",
            use_textfsm=False,
            enable=enable,
        )
        task.run(task=netmiko_send_command, name="display vlan brief", command_string="display vlan brief", use_textfsm=False, enable=enable)
        task.run(
            task=netmiko_send_command,
            name="display mac-address",
            command_string="display mac-address",
            use_textfsm=False,
            enable=enable,
        )
        task.run(task=netmiko_send_command, name="display ip vpn-instance", command_string="display ip vpn-instance", use_textfsm=False, cmd_verify=False, enable=enable) # See https://github.com/ktbyers/netmiko/issues/2707
        task.run(
            task=netmiko_send_command, name="display ip interface", command_string="display ip interface", use_textfsm=False, enable=enable
        )
        task.run(
            task=netmiko_send_command, name="display stp", command_string="display stp", use_textfsm=False, enable=enable
        )
        task.run(
            task=netmiko_send_command, name="display port trunk", command_string="display port trunk", use_textfsm=False, enable=enable
        )
        task.run(
            task=netmiko_send_command, name="ddisplay link-aggregation verbose", command_string="ddisplay link-aggregation verbose", use_textfsm=False, enable=enable
        )
        task.run(
            task=netmiko_send_command, name="display vrrp", command_string="display vrrp", use_textfsm=False, enable=enable
        )
        task.run(
            task=netmiko_send_command, name="display ospf peer", command_string="display ospf peer", use_textfsm=False, enable=enable
        )
        task.run(
            task=netmiko_send_command, name="display bgp peer", command_string="display bgp peer", use_textfsm=False, enable=enable
        )
        task.run(
            task=netmiko_send_command, name="display ip routing-table", command_string="display ip routing-table", use_textfsm=False, enable=enable
        )
        task.run(
            task=netmiko_send_command, name="display ip routing-table|display ip routing-table vpn-instance", command_string="display ip routing-table vpn-instance", use_textfsm=False, enable=enable
        )

    # Run the playbook
    aggregated_results = filtered_devices.run(task=multiple_tasks)

    # Print the result
    print_result(aggregated_results)

    for key, multi_result in aggregated_results.items():
        vrfs = ["default"] # Adding default VRF
        current_nr = nr.filter(F(name=key))

        # MultiResult is an array of Result
        for result in multi_result:
            if result.name == "multiple_tasks":
                # Skip MultipleTask
                continue

            address = result.host.dict()["hostname"]
            discoverable = models.Discoverable.objects.get(address=address, mode=f'{mode}_{platform}')
            discoverable.last_discovered_at = timezone.now() # Update last_discovered_at
            discoverable.save()

            # Log locally
            log = functions.log_create(
                discoverable=discoverable,
                raw_output=result.result,
                request=result.name,
            )

            # Save log for later
            logs.append(log)

            # Save VRF list for later
            if result.name == "display ip vpn-instance":
                try:
                    vrf_parsed_output = functions.parse_netmiko_output(result.result, platform=platform, command=result.name)
                except:
                    vrf_parsed_output = []
                for entry in vrf_parsed_output:
                    vrfs.append(entry["name"])

        # Additional commands out of the multi result loop
        def additional_tasks(task):
            """
            Define additional tasks for the playbook.
            """
            # Per VRF commands
            for vrf in vrfs:
                if vrf == "default":
                    # Default VRF has no name
                    task.run(task=netmiko_send_command, name="display arp", command_string="display arp", use_textfsm=False, enable=enable)
                else:
                    task.run(task=netmiko_send_command, name=f'display arp|display arp vpn-instance {vrf}', command_string=f'display arp vpn-instance {vrf}', use_textfsm=False, enable=enable)
                    task.run(task=netmiko_send_command, name=f'display ip vpn-instance instance-name|display ip vpn-instance instance-name {vrf}', command_string=f'display ip vpn-instance instance-name {vrf}', use_textfsm=False, enable=enable)

        # Run the additional playbook
        additional_aggregated_results = current_nr.run(task=additional_tasks)

        # Print the result
        print_result(additional_aggregated_results)

        for key, additional_multi_result in additional_aggregated_results.items():
            # MultiResult is an array of Result
            for result in additional_multi_result:
                if result.name == "additional_tasks":
                    # Skip MultipleTask
                    continue

                # Log locally
                log = functions.log_create(
                    discoverable=discoverable,
                    raw_output=result.result,
                    request=result.name,
                )

                # Save log for later
                logs.append(log)
