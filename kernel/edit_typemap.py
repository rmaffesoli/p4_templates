#!/usr/bin/env python

"""edit_permissions doc string"""

from __future__ import print_function

import subprocess

def get_typemap():
    with subprocess.Popen(
        ["p4", "typemap", "-o"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ) as proc:

        type_stdout = proc.communicate()[0]

        type_string = type_stdout.decode()
        type_string = type_string.replace("\t", "")
        type_string = type_string.replace("\r", "\n")
        type_string = type_string.replace("\n\n", "\n")
        type_string = type_string.split("TypeMap:\n")[1]
        
        

        raw_type_list = [_ for _ in type_string.split("\n") if _ not in ["", "\n"]]
        type_dict = {}

        for entry in raw_type_list:
            while "  " in entry:
                entry = entry.replace("  ", " ")

            type_key, type_value = [_.replace("\n", "") for _ in entry.split(" ")]

            if type_key not in type_dict:
                type_dict[type_key] = set()

            type_dict[type_key].add(type_value)

        return type_dict


def add_type(type_dict, type_key, type_value):
    if type_key not in type_dict:
        type_dict[type_key] = set()

    type_dict[type_key].add(type_value)
    return type_dict


def save_typemap(type_dict, dryrun):
    typemap_lines = ["TypeMap:"]
    for file_type in sorted(type_dict):
        for file_path in sorted(type_dict[file_type]):
            entry_line = "\t{type} {path}".format(type=file_type, path=file_path)

            typemap_lines.append(entry_line)
    if dryrun:
        print('='*40)
        print("Projected Typemap edits:") 
        print('\n'.join(typemap_lines))
        print('='*40)
    else:
        with subprocess.Popen(
            ["p4", "typemap", "-i"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ) as proc:
            prot_stdout = proc.communicate(
                input=bytes("\n".join(typemap_lines), "utf-8")
            )[0]
            print(prot_stdout.decode())


def append_new_typemap_entry(type_entries, dryrun=0):
    existing_types = get_typemap()
    for file_type in type_entries:
        for file_path in type_entries[file_type]:
            existing_types = add_type(existing_types, file_type, file_path)

    save_typemap(existing_types, dryrun)

