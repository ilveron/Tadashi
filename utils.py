import subprocess
import re
from constants import *
import os
from datetime import datetime, timezone


def is_os_linux():
    return os.name == "posix"


def sanitize_atoms(atoms):
    to_return = []
    for atom in atoms:
        sanitized_atom = atom.replace(" ", "")
        if sanitized_atom != "":
            sanitized_atom = sanitized_atom + "."  # add the dot at the end
            to_return.append(sanitized_atom)
    return to_return


def later_timepoint_exists(timepoints, new_timepoint):
    for t in timepoints:
        if t > new_timepoint:
            return True
    return False


def get_log_atoms(filename):
    to_return = {}
    lines = subprocess.check_output(f"cat {LOGS}/{filename}.log", shell=True).decode("utf-8").split("\n")
    for line in lines:
        if line != "":
            # divide the line in two parts: timepoint and its related input
            result = re.search(r'(\S+)\s(.*)', line)
            if result is not None:  # if said timestamp has some atoms in it
                timepoint = convert_to_unix(result.group(1))
                related_input = result.group(2)

                atoms_split = related_input.split(";")
                atoms = sanitize_atoms(atoms_split)

                # TODO: I don't know if I can assume that logs do not have late streams
                if timepoint not in to_return:
                    to_return[timepoint] = atoms
                elif not later_timepoint_exists(to_return.keys(), timepoint):  # Add only if there is no later timepoint
                    to_return[timepoint] = to_return[timepoint] + atoms
    return to_return


def convert_to_unix(date):
    dt = datetime.fromisoformat(date)
    # we need to do this operation to cancel the timezone
    timepoint = int((dt - datetime(1970, 1, 1)).total_seconds())
    return timepoint


# reverse the method above to convert from unix to iso, taking into account the timezone
def convert_to_iso(timepoint):
    # Crea un oggetto datetime con il fuso orario UTC
    dt = datetime.fromtimestamp(timepoint, tz=timezone.utc)
    # Rimuovi il fuso orario per ottenere una data ingenua
    dt = dt.replace(tzinfo=None)
    return dt.isoformat()


def is_service_atom(atom):
    for service_atom in SERVICE_ATOMS:
        if re.search(service_atom, atom) is not None:
            return True
    return False
