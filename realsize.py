import os
import subprocess
from arg_processor import arg_processor
from enum import Enum
from sys import argv, exit

relative_root = ""
descriptions = []
max_depth = 0
unit_select = None
measurements = [[" B"," KiB"," MiB"," GiB"], [" B"," kB"," MB"," GB"]]

class Units(Enum):
    BINARY = 0
    DECIMAL = 1

def convert_bytes_to_units(bytes, which_unit):
    unit_list = measurements[which_unit]
    i = 0
    factor = 2**10 if "KiB" in unit_list else 10**3
    while i < len(unit_list):
        if bytes < factor:
            return str(round(bytes,1)) + unit_list[i]

        bytes = bytes / factor 
        i += 1

    return "Unknown"

'''
    print("├── Folder1")

    print("│   ├── File1")

    print("└── Folder2")
'''

def go_into_directory(dirpath, curr_depth):
    # the "real" base case -- if we are at max depth as defined by user, go no further
    if curr_depth < 0:
        return 0

    local_byte_size = 0
    prefix_dir = os.path.basename(dirpath)

    with os.scandir(dirpath) as entries:
        # list out any subdirectories/folders within arms' reach
        folder_list = [] 
        for entry in entries:
            # "base case" for getting single file size
            if entry.is_file():
                file_size = os.path.getsize(entry.path)
                local_byte_size += file_size
                relpath = os.path.join(prefix_dir, entry.name)
                print(f"{convert_bytes_to_units(file_size, Units.BINARY.value):>14} | {relpath}")

            # "recursive case" for entering subdirectories 
            elif entry.is_dir():
                folder_list.append(f"{prefix_dir}/{entry.name}")
                subdir_byte_size = go_into_directory(entry.path, curr_depth-1)
                local_byte_size += subdir_byte_size 

        num_folders = len(folder_list)
        if num_folders > 0:
            folder_list_header = f"{num_folders:>6} folder{'s' if num_folders > 1 else ''} in {os.path.basename(dirpath)} "
            print(folder_list_header)
            entry_margin = len(folder_list_header) - 3
            for folder in folder_list:
                print(f"{' '*entry_margin}../{os.path.basename(folder)}/")

    # print(f"{convert_bytes_to_units(local_byte_size, Units.BINARY.value)} total in {prefix_dir}")
    if local_byte_size > 0:
        descriptions.append(f"{convert_bytes_to_units(local_byte_size, Units.BINARY.value)} total in {prefix_dir} at depth={abs(curr_depth - max_depth)}")
    return local_byte_size


def main():
    global relative_root, max_depth 
    parser = arg_processor()

    (options, args) = parser.parse_args()

    total_byte_size = 0
    if not args:
        parser.print_help()
        exit(0)
    root_dir = os.path.abspath(args[0])
    relative_root = os.path.basename(root_dir)
    unit = Units.DECIMAL.value if options.use_decimal else Units.BINARY.value

    if os.path.isfile(root_dir):
        file_size = os.path.getsize(root_dir)
        print(f"{convert_bytes_to_units(file_size, unit):>14} | {root_dir}")

    elif os.path.isdir(root_dir):
        total_byte_size += go_into_directory(root_dir, options.max_depth)

        if descriptions:
            pformat = '\n'.join(sorted([f"{' '*15}{desc:<50}" for desc in descriptions], key=lambda x: x.strip().split(' ')[-1].strip().split('=')[-1], reverse=False))
            print(pformat)

        print(f"Total: {convert_bytes_to_units(total_byte_size, unit)}")

    else:
        print("path does not exist!")
        exit(-1)
        

if __name__ == "__main__":
    main()
