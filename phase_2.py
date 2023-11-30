#!/usr/bin/python3

"""
Phase 2 of the Tadashi pipeline:
    For each folder in tadashi (created by Phase 1), hence for each encoding:
        For each timepoint extracted from the input files:
            - Check whether the atoms in the logs are in the input file
            - Generate a temporary asp file with the full rewriting (input + rewriting)
            - Run DLV on the temporary asp file (OPTS: -n=0 --printonlyoptimum --silent=0)
            - Collect the output of DLV (prog_name.answersets)

"""

from utils import *
import re


def main():
    if not is_os_linux():
        raise Exception("This script is only compatible with Linux")

    filenames_list = subprocess.check_output(f'cd tadashi && ls -d */ | sed "s/\///"', shell=True).decode("utf-8").split("\n")[
                     0:-1]
    print("PHASE 2 - DLV2 ANSWER SETS COMPUTATION")
    for filename in filenames_list:
        print(f"Processing {filename}")
        input_atoms = get_input_atoms(filename)
        compose_asp_files(filename, input_atoms)
        compute_answersets(filename, input_atoms.keys())
        remove_asp_files(filename)


def remove_asp_files(filename):
    subprocess.call(f"rm -rf tadashi/{filename}/asp_encodings", shell=True)


def compute_answersets(filename, timepoints):
    subprocess.call(f"rm -rf tadashi/{filename}/answersets", shell=True)
    subprocess.call(f"mkdir tadashi/{filename}/answersets", shell=True)
    for timepoint in timepoints:
        actual_dlv2_options = DLV2_OPTS
        dlv2_encoding_path = f"tadashi/{filename}/asp_encodings/{filename}_{timepoint}.asp"

        is_incoherent = True
        while is_incoherent:
            if has_weak(dlv2_encoding_path):
                actual_dlv2_options = DLV2_OPTS + " --printonlyoptimum"

            if not has_external_atom(filename):
                subprocess.call(
                    f"./{DLV2} {dlv2_encoding_path} {actual_dlv2_options} > " +
                    f"tadashi/{filename}/answersets/{filename}_{timepoint}.answerset", shell=True)
            else:
                external_definition_path = f"tadashi/{filename}/{filename}.py"
                subprocess.call(
                    f"./{DLV2_PYTHON} {dlv2_encoding_path} {external_definition_path} {actual_dlv2_options}" +
                    f" > tadashi/{filename}/answersets/{filename}_{timepoint}.answerset",
                    shell=True)

            answerset_file_path = f"tadashi/{filename}/answersets/{filename}_{timepoint}.answerset"
            # check if incoherent
            res = subprocess.check_output(["head", "-1", f"{answerset_file_path}"]) \
                .decode("utf-8").split("\n")

            if "INCOHERENT" == res[0]:
                compose_deterministic_asp_file(filename, f"{filename}_{timepoint}.asp")
            else:
                is_incoherent = False


def compose_deterministic_asp_file(encoding_name, asp_filename):
    to_write = []
    path = f"tadashi/{encoding_name}/asp_encodings/{asp_filename}"
    with open(path, "r") as f:
        for row in f:
            if '|' in row or re.match(r'^ *:-', row) or re.match(r'^ *:~', row):
                # ignore non-determinism related stuff from the asp file
                continue
            to_write.append(row)

    with open(path, "w") as f:
        for row in to_write:
            f.write(row)


def has_weak(dlv2_encoding_path):
    with open(dlv2_encoding_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if ":~" in line:
                return True
    return False


def has_external_atom(filename):
    if f"{filename}.py" in os.listdir(f"tadashi/{filename}"):
        return True
    return False


def compose_asp_files(filename, input_atoms):
    subprocess.call(f"rm -rf tadashi/{filename}/answersets", shell=True)
    subprocess.call(f"mkdir tadashi/{filename}/asp_encodings", shell=True)

    timepoints = input_atoms.keys()

    for timepoint in timepoints:
        with open(f"tadashi/{filename}/asp_encodings/{filename}_{timepoint}.asp", "w") as f:
            f.write(" ".join(input_atoms[timepoint]) + "\n")
            f.write(subprocess.check_output(f"cat tadashi/{filename}/rewriting.asp", shell=True).decode("utf-8"))


def get_input_atoms(filename):
    to_return = {}

    # from input files we extract timepoints
    # we must do two reverses, one before cutting and one after
    # because encodings with one or multiple underscores in the name were creating problems
    timepoints = subprocess.check_output(f"ls tadashi/{filename}/inputs/input_* | rev | cut -d'_' -f 1 | rev",
                                     shell=True).decode("utf-8").split("\n")[0:-1]

    # convert all elements of timepoints to int
    timepoints = list(map(int, timepoints))
    for timepoint in timepoints:
        lines = subprocess.check_output(f"cat tadashi/{filename}/inputs/input_{timepoint}", shell=True) \
            .decode("utf-8").split("\n")[0:-1]
        for line in lines:
            atoms_split = line.split(".")
            atoms = sanitize_atoms(atoms_split)
            if timepoint not in to_return:
                to_return[timepoint] = atoms
            else:
                to_return[timepoint] = to_return[timepoint] + atoms

        # if input gives no atoms
        if timepoint not in to_return:
            to_return[timepoint] = []
        else:
            # remove duplicates
            to_return[timepoint] = list(set(to_return[timepoint]))

    return to_return


if __name__ == '__main__':
    main()
