#!/usr/bin/python3

import subprocess
import os

JAR = "I-DLV-sr-v2.0.0.jar"
LOGS = "input_logs"
ENCODINGS = "idlvsr_encodings"

def main():
    if not is_os_linux():
        raise Exception("This script is only compatible with Linux")

    filenames_list = subprocess.check_output(f"ls {ENCODINGS} | cut -d'.' -f 1", shell=True).decode("utf-8").split("\n")[0:-1]
    
    #if subprocess.check_output("ls {LOGS} | cut -d'.' -f 1", shell=True).decode("utf-8").split("\n")[0:-1] != filename_list:
    #    raise Exception("The input logs and the {ENCODINGS} are not the same")

    create_main_folder()

    for filename in filenames_list:
        print(f"Processing {filename}.idlvsr")
        if not log_exists(filename):
            print (f"There is no log file for the encoding {filename}.idlvsr. Skipping...")
            continue

        # create the folder
        subprocess.call(f"mkdir tadashi/{filename}", shell=True)

        run_idlv_sr(filename)

        collect_files(filename)

def create_main_folder():
    subprocess.call("mkdir tadashi", shell=True)

def log_exists(filename):
    return subprocess.check_output(f"find {LOGS} -name {filename}.log", shell=True).decode("utf-8").split("\n")[0] == f"{LOGS}/{filename}.log"

def run_idlv_sr(filename):
    subprocess.call(f'java -jar {JAR} --log={LOGS}/{filename}.log --program={ENCODINGS}/{filename}.idlvsr --export-idlv-input --json-output --parallelism=4 > "./tadashi/{filename}/{filename}.json" 2> /dev/null', shell=True)

def collect_files(filename):
    # in reasoner_input folder take files ending with _ and all the numbers after it and move it to tadashi/{filename} 
    input_epochs = subprocess.check_output(f'find reasoner_input -name "input_time*" | cut -d"_" -f 6', shell=True).decode("utf-8")[0:-1].split("\n")

    for e in input_epochs:
        # merge the input files that refer to the same epoch
        subprocess.call(f'cat reasoner_input/*_{e} > tadashi/{filename}/input_{e}', shell=True)
    
    # merge rewritings
    subprocess.call(f'cat reasoner_input/rewriting* > tadashi/{filename}/rewriting.asp', shell=True)

def is_os_linux():
    return os.name == "posix"

if __name__ == "__main__":
    main()