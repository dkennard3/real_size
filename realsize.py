import os
from arg_processor import arg_processor
from enum import Enum
from sys import argv, exit

relative_root = ""
descriptions = []
max_depth, num_files, all_files = 0, 0, 0
num_folders, all_folders = -1, 0
folder_sizes = {}
unit_select = 0 
show_hidden = True
last_dir_name = ""
entry_indent_length = len('├── ') 
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
TODO: 
    * consider EDGE_CASE where file has no file extension
        - split by '.', grab [-1]
        - if there aren't 2 to 4 chars,
            - truncate X number of chars off file_name, replace with '...', done.

    * allow flag option for BRIEF output, only showing byte counts but not the tree branches

    * set hard recursion limit to 10+ (tbd) levels

    * adjust wording on [X folders, Y files, Z bytes in total] to be more contextual
        * (AKA don't print Y files if there are none, say subfolders instead of folders 
          for all except the starting dir specified by user)

    * try-catch for no-read restrictions in a given folder's permissions
'''


'''
    print("├── Folder1")

    print("│   ├── File1")

    print("└── Folder2")
'''

def go_into_directory(dirpath, curr_depth):
    # the "real" base case -- if we are at max depth as defined by user, go no further
    if curr_depth < 0:
        return 0

    global last_dir_name, entry_indent_length, num_files, num_folders, folder_sizes
    global all_folders, all_files
    local_byte_size = 0
    curr_indent_space = ' ' * entry_indent_length * abs(curr_depth-max_depth)
    prefix_dir = os.path.basename(dirpath)
    with os.scandir(dirpath) as entries:
        # list out any subdirectories/folders within arms' reach
        num_folders = 0
        num_files = 0
        e = sorted([entry for entry in entries], key= lambda x: ( x.is_dir(), x.name), reverse=False)
        for entry in e:
            # ignore hidden files/dirs
            # if entry.name[0] == ".":
            #     continue
            if entry.name[0] == "." and not show_hidden:
                continue
            # "base case" for getting single file size
            if entry.is_file():
                num_files += 1
                all_files += 1
                file_size = os.path.getsize(entry.path)
                if last_dir_name not in folder_sizes:
                    folder_sizes[last_dir_name] = 0 

                folder_sizes[last_dir_name] += file_size
                local_byte_size += file_size
                f_size_val, f_size_unit = convert_bytes_to_units(file_size, unit_select).split(" ")
                shown_name = entry.name

                '''
                TODO: replace hard-coded 23 value to configurable generic
                '''
                # truncation rules for long filenames
                if len(entry.name) > 23:
                    if "." in entry.name:
                        chunks = entry.name.split(".")
                        fileExt = chunks[-1]

                        if len(fileExt) >= 2 and len(fileExt) <= 4:
                            shown_name = entry.name[:20] + "..." + chunks[-1]
                        else:
                            shown_name = entry.name[:23] + "..."
                    else:
                        shown_name = entry.name[:23] + "..."

                desc_indent = len(curr_indent_space) + len(shown_name)
                # desc_indent_space = ' '*desc_indent
                print(f"{curr_indent_space}├── {shown_name}{'_'*(40-desc_indent)}--> {f_size_val}{' '*(5-len(f_size_val))} {f_size_unit}")

            # "recursive case" for entering subdirectories 
            elif entry.is_dir() and last_dir_name != dirpath:
                folder_sizes[entry.name] = 0
                num_folders += 1
                all_folders += 1
                last_dir_name = entry.name 
                print(f"{curr_indent_space}├── {entry.name}")
                # folder_list.append(f"{entry.name}")
                subdir_byte_size = go_into_directory(entry.path, curr_depth-1)
                local_byte_size += subdir_byte_size 
        # print(f"{curr_indent_space}{' '*4}[{num_folders} folders, {num_files} files" + (f", {convert_bytes_to_units(folder_sizes[last_dir_name], unit_select)} in total]" if num_files > 0 else "]"))
        print(f"{curr_indent_space}{' '*4}[{num_folders} folders, {num_files} files" + (f", {convert_bytes_to_units(local_byte_size, unit_select)} in total]" if num_files > 0 else "]"))
        # print(folder_sizes)

    # if local_byte_size > 0:
    #     print(f"{convert_bytes_to_units(local_byte_size, Units.BINARY.Units.BINARY.valuevalue)} total in {prefix_dir} at depth={abs(curr_depth - max_depth)}")
    return local_byte_size


def main():
    global relative_root, max_depth, last_dir_name
    global all_folders, all_files, show_hidden
    parser = arg_processor()

    (options, args) = parser.parse_args()

    total_byte_size = 0
    if not args:
        parser.print_help()
        exit(0)
    root_dir = os.path.abspath(args[0])
    relative_root = os.path.basename(root_dir)
    unit_select = Units.DECIMAL.value if options.use_decimal else Units.BINARY.value
    show_hidden = options.show_hidden

    if os.path.isfile(root_dir):
        file_size = os.path.getsize(root_dir)
        print(f"{convert_bytes_to_units(file_size, unit_select):>14} | {root_dir}")

    elif os.path.isdir(root_dir):
        max_depth = options.max_depth
        last_dir_name = relative_root
        total_byte_size += go_into_directory(root_dir, options.max_depth)

        # if descriptions:
        #     pformat = '\n'.join(sorted([f"{' '*15}{desc:<50}" for desc in descriptions], key=lambda x: x.strip().split(' ')[-1].strip().split('=')[-1], reverse=False))
        #     print(pformat)

        print(f"[{all_folders} folders, {all_files} files, {convert_bytes_to_units(total_byte_size, unit_select)} in total]")

    else:
        print("path does not exist!")
        exit(-1)
        

if __name__ == "__main__":
    main()
