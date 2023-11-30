#!/usr/bin/python3

"""
    Phase 3 of the Tadashi pipeline:
        For each folder in tadashi (created by Phase 1), hence for each encoding:
            For each timepoint:
                - Check whether all atoms in idlvsr answerstream are in the answer set of DLV
                - If a cost is present in the idlvsr answerstream, check whether the cost is the same in the answer set
                  of DLV
                - If DLV's result is INCOHERENT, check whether the idlvsr answerstream contains at least what is in the
                  log
                - Writes to the related report file the result of the comparison
"""

from utils import *
import json


def main():
    if not is_os_linux():
        raise Exception("This script is only compatible with Linux")

    # all folder names in tadashi except report.txt, hence the list of all encodings processed by the suite
    filenames_list = subprocess.check_output(f'cd tadashi && ls -d */ | sed "s/\///"', shell=True).decode("utf-8") \
        .split("\n")[0:-1]

    print("PHASE 3 - I-DLV-SR ANSWER STREAMS COMPARISON")
    remove_last_report()
    for filename in filenames_list:
        print(f"Processing {filename}")

        file_is_processed_correctly = True
        timepoints = []
        set_timepoints(filename, timepoints)

        # map: timepoint -> costs
        idlvsr_costs = {}

        # map: timepoint -> answerstream 
        idlvsr_answer_streams = {}

        set_answer_streams_and_costs(filename, idlvsr_answer_streams, idlvsr_costs)

        log_atoms = get_log_atoms(filename)

        failed_timepoints = []

        for timepoint in timepoints:
            if timepoint not in log_atoms:
                log_atoms_for_this_timepoint = []
            else:
                log_atoms_for_this_timepoint = log_atoms[timepoint]

            costs_for_this_timepoint = []

            if timepoint in idlvsr_costs:
                costs_for_this_timepoint.extend(idlvsr_costs[timepoint])

            if process_timepoint(timepoint, filename, idlvsr_answer_streams[timepoint],
                             costs_for_this_timepoint, log_atoms_for_this_timepoint):
                print(f"\t\ttimepoint {timepoint} is correct")
            else:
                print(f"\t\ttimepoint {timepoint} is NOT correct")
                file_is_processed_correctly = False
                failed_timepoints.append(timepoint)

        write_report_record(filename, file_is_processed_correctly, failed_timepoints)


def process_timepoint(timepoint, filename, answer_stream, answer_stream_costs, log_atoms_for_this_timepoint):
    print(f"\tProcessing timepoint {timepoint}")

    answersets_list = []
    answer_set_costs = []

    set_answersets_and_costs_for_this_timepoint(filename, timepoint, answersets_list, answer_set_costs)

    print(f"\t\tDLV2 COSTS: {answer_set_costs}")
    print(f"\t\tIDLVSR COSTS: {answer_stream_costs}")

    for answerset in answersets_list:
        answerset.extend(log_atoms_for_this_timepoint)

        # make all the atoms in every answerset of answersets_list unique
    answersets_list = [list(set(answerset)) for answerset in answersets_list]

    # remove atoms that are service atoms
    answersets_list = [[atom for atom in answerset if not is_service_atom(atom)] for answerset in answersets_list]

    print(f"\t\tIDLVSR AS:\t{answer_stream}")
    print(f"\t\tDLV2 AS LIST:\t{answersets_list}")

    if not check_costs(answer_stream_costs, answer_set_costs):
        return False

    for answerset in answersets_list:
        # every atom in the answerstream must be in the answerset and viceversa
        result = all(atom in answerset for atom in answer_stream) and all(atom in answer_stream for atom in answerset)
        if result:
            return True
    return False


def set_answersets_and_costs_for_this_timepoint(filename, timepoint, answersets_list, costs_list):
    answersets_file_list = subprocess.check_output(
        f"cat tadashi/{filename}/answersets/{filename}_{timepoint}.answerset", shell=True) \
                               .decode("utf-8").split("\n")[0:-1]

    for answerset in answersets_file_list:
        is_a_cost = re.search(r"COST\s(.+)", answerset)
        if is_a_cost:
            costs_string = is_a_cost.group(1)
            costs_list.extend(costs_string.split(" "))
        elif answerset.startswith("{"):
            answerset = answerset.replace("{", "").replace("}", "")
            sanitized_answerset = sanitize_atoms(answerset.split(", "))
            if sanitized_answerset not in answersets_list:
                answersets_list.append(sanitized_answerset)


def set_answer_streams_and_costs(filename, idlvsr_answer_streams, idlvsr_costs):
    json_path = f"tadashi/{filename}/{filename}.json"

    with open(json_path, 'r') as file:
        # every line will be the answer for a single timepoint
        for line in file:
            data = json.loads(line)
            timestamp = int(convert_to_unix(data.get("timestamp", "")))

            answers = data.get("answers", [])

            # if the answer isn't empty (empty list means no atoms)
            if answers[0]:
                atoms_split = answers[0].split(", ")

                last_atom = atoms_split[-1]

                # if the last atom contains the cost, remove it from the list and save it
                res = re.search(r"(.*)?\n\tCOST\s(.*?)\n\tOPTIMUM", last_atom)
                if res is not None:
                    costs_string = res.group(2)
                    costs_list = costs_string.split(" ")
                    idlvsr_costs[timestamp] = costs_list
                    atoms_split[-1] = res.group(1)  # replace the last atom with the one without the cost

                # eventually sanitize the atoms
                atoms = sanitize_atoms(atoms_split)
            else:
                atoms = []

            idlvsr_answer_streams[timestamp] = atoms


""" I-DLV-SR and DLV2 handle costs output in a slightly different way: I-DLV-SR usually seems to output 
    more cost levels at cost 0 than DLV2. This function simply takes all non-zero costs from both lists,
    and checks whether they are equal. If they are, the costs are the same, otherwise they aren't. """


def check_costs(answer_stream_costs, answer_set_costs):
    non_zero_dlv2_costs = [cost.split('@')[0] for cost in answer_set_costs if not cost.startswith("0")]
    non_zero_idlvsr_costs = [cost.split('@')[0] for cost in answer_stream_costs if not cost.startswith("0")]

    if non_zero_dlv2_costs != non_zero_idlvsr_costs:
        return False
    return True


def remove_last_report():
    print("Removing last report")
    subprocess.call(f"rm -rf tadashi/report.txt", shell=True)


def set_timepoints(filename, timepoints):
    timepoints.extend(subprocess.check_output(f"ls tadashi/{filename}/inputs/input_* | rev | cut -d'_' -f 1 | rev",
                                          shell=True).decode("utf-8").split("\n")[0:-1])
    # convert all elements of timepoints to int
    timepoints[:] = list(map(int, timepoints))


def write_report_record(filename, file_is_processed_correctly, failed_timepoints):
    if file_is_processed_correctly:
        to_write = f"{filename:<35} CORRECT"
    else:
        to_write = f"{filename:<35} NOT CORRECT ({[str(convert_to_iso(timepoint)) for timepoint in failed_timepoints]})"
    # write the results to the report file
    with open(f"tadashi/report.txt", "a") as f:
        f.write(f"{to_write}\n")


if __name__ == '__main__':
    main()
