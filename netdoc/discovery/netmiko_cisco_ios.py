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
    Discovery Cisco IOS devices
    """
    mode = "netmiko"
    platform = "cisco_ios"
    filtered_devices = nr.filter(platform=platform)
    enable=True

    # Define commands
    commands = [
        # Config (bool), CMD (str), Ingestor
        (True,  "show running-config"),
        (False, "show version"),
        (False, "show logging"),
        (False, "show interfaces"),
        (False, "show cdp neighbors detail"),
        (False, "show lldp neighbors detail"),
        (False, "show vlan"),
        (False, "show mac address-table dynamic"),
        (False, "show vrf"),
        (False, "show ip interface"),
        (False, "show etherchannel summary"),
        (False, "show interfaces switchport"),
        (False, "show spanning-tree"),
        (False, "show interfaces trunk"),
        (False, "show standby"),
        (False, "show vrrp"),
        (False, "show glbp"),
        (False, "show ip ospf neighbor"),
        (False, "show ip eigrp neighbors"),
        (False, "show ip bgp neighbors"),
    ]

    # Define tasks
    def multiple_tasks(task):
        """
        Define tasks for the playbook.
        """
        for command in commands:
            functions.nornir_add_netnmiko_task(
                task, command=commands[1], configuration=commands[0], enable=enable,
            )

    # Run the playbook
    aggregated_results = filtered_devices.run(task=multiple_tasks)

    # Print results
    print_result(aggregated_results)

    # Analyze results
    for key, multi_result in aggregated_results.items():
        current_nr = nr.filter(F(name=key)) # Save current filter
        vrfs = ["default"] # Adding default VRF

        # MultiResult is an array of Result
        for result in multi_result:
            # Log locally
            log = functions.log_result(result)

            # Save VRF list for later
            if log and log.command = "show vrf" and log.parsed:
                for entry in log.parsed_output:
                    vrfs.append(entry["name"])

        # Define additionals commands
        additional_commands = []
        for vrf in vrfs:
            if vrf == "default":
                additional_commands.extend([
                    (False,  "show ip arp"),
                    (False,  "show ip route"),
                ]
            else:
                additional_commands.extend([
                    (False, f"show ip arp|vrf {vrf}"),
                    (False, f"show ip route|vrf {vrf}"),
                ]

        # Additional commands out of the multi result loop
        def additional_tasks(task):
            """
            Define additional tasks for the playbook.
            """
            for command in additional_commands:
                functions.nornir_add_netnmiko_task(
                    task, command=commands[1], ntc_template=commands[2], configuration=commands[0], enable=enable,
                )

        # Run the additional playbook
        additional_aggregated_results = current_nr.run(task=additional_tasks)

        # Print the result
        print_result(additional_aggregated_results)

        # Analyze results
        for key, additional_multi_result in additional_aggregated_results.items():
            # MultiResult is an array of Result
            for result in additional_multi_result:
                # Log locally
                log = functions.log_result(result)
