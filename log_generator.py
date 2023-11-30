#!/usr/bin/python3
from utils import convert_to_iso
import sys


def main():
    print(sys.argv)
    if len(sys.argv) != 4:
        print("Usage: python3 log_generator.py <log_file_name> <start_epoch> <end_epoch>")
        sys.exit(1)
    log_file_name = sys.argv[1]
    start_epoch = int(sys.argv[2])
    end_epoch = int(sys.argv[3])

    if start_epoch > end_epoch:
        print("Start epoch must be less than end epoch")
        sys.exit(1)

    to_write = ""

    for epoch in range(start_epoch, end_epoch+1):
        to_write += convert_to_iso(epoch) + "\n"

    with open(log_file_name, "w") as f:
        f.write(to_write)


if __name__ == '__main__':
    main()
