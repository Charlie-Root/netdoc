from nornir_netmiko.tasks import netmiko_send_command
import re
import os
import importlib
from netmiko.utilities import get_structured_data
from netdoc.models import DiscoveryLog
from netdoc.ingestors.functions import log_ingest

INVALID_RE = [
    # WARNING: must specify ^/$ or a very unique string not found in valid outputs
    r"^$", # Empty result
    r"^\^", # Cisco Error (e.g. "^Note: ")
    r"^% ", # Generic Cisco error (e.g. "% Invalid command")
    r"^\s*\^\n%", # Cisco Error (e.g. "^\n% Invalid...")
    r"^No spanning tree instances exist", # Cisco
    # r"% Invalid input detected", # Cisco (with ^ the % is not at the beginning)
    # r"% Invalid command at", # Cisco (with ^ the % is not at the beginning)
    r"% \w* is not enabled$", # Cisco XR put datetime before the error
    r"% \w* not active$", # Cisco XR put datetime before the error
]


def nornir_add_netnmiko_task(task, command, ingestor=None, configuration=False, enable=True):
    """Add a netmiko task with metadata into nornir

    Parameters:
    ----------
    task : ???
    command: str
        The command to be run via netmiko.
    ingestor: str, optional
        The command use to ingest data. If None, output won't be parsed/ingested.
    configuration: bool, optional
        True if the output contains the running/startup configuration.
    enable: bool, optional
        True if enable command is required to elevate privileges.
    """

    attributes = {
        # Stored as task name and used in the discovery task
        # If "|" in command, split and use it as ingestor
        'task': 'netmiko_send_command',
        'command': command.replace("|", ""),
        'ingestor': command.split("|")[0] if "|" in command, else command.replace("|", ""),
        'configuration': configuration;
        'enable': enable,
    }

    task.run(
        task=netmiko_send_command,
        name=json.dumps(attributes),
        command_string=cmd,
        use_textfsm=False,
        enable=enable,
    )


# Log locally
def log_result(result):
    if result.name == "multiple_tasks":
        # Skip MultipleTask
        return False

    # Update discoverable
    address = result.host.dict()["hostname"]
    discoverable = models.Discoverable.objects.get(address=address)
    discoverable.last_discovered_at = timezone.now() # Update last_discovered_at
    discoverable.save()

    # Load attributes
    attributes = json.loads(result.name)

    # Add log
    log = functions.log_create(
        command=attributes["command"],
        configuration=attributes["configuration"],
        discoverable=discoverable,
        request=attributes["ntc_template"],
        raw_output=result.result,
    )

    # Try to parse
    try:
        log = log_parse(log)
    except:
        pass

    # # Try to ingest
    # try:
    #     log = log_ingest(log)
    # except:
    #     pass
    # TODO: should review before create/update

    return log


def log_parse(log):
    parsed = False
    parsed_output = None
    try:
        framework = log.discoverable.mode.split('_').pop(0)
        platform = '_'.join(log.discoverable.mode.split('_')[1:])
    except:
        raise ModeNotDetected
    if framework == 'netmiko':
        parsed_output = parse_netmiko_output(log.raw_output, platform=platform, command=log.request)
        parsed = True
    else:
        raise ModeNotDetected

    log.parsed = parsed
    log.parsed_output = parsed_output
    log.save()
    return log


def parse_netmiko_output(output, command=None, platform=None):
    try:
        parsed_output = get_structured_data(output, platform=platform, command=command)
        if not isinstance(parsed_output, dict) and not isinstance(parsed_output, list):
            raise FailedToParse
    except Exception:
        raise FailedToParse
    return parsed_output


def valid_output(output):
    for regex in INVALID_RE:
        # Check if the output is valid
        if re.search(regex, output):
            return False
    return True
