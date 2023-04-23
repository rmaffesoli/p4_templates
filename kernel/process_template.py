#!/usr/bin/env python

"""process_template doc string"""

from __future__ import print_function

import argparse
import os

from create_depot import create_depot
from create_stream import create_stream
from create_group import create_group
from create_user import create_user
from create_branch import create_branch, populate_branch, delete_branch
from edit_permissions import append_new_protections
from edit_typemap import append_new_typemap_entry
from utils import set_default, write_json, read_json, gather_parameters, substitute_parameters


def process_template(template):

    append_new_typemap_entry(template.get("types", {}))

    append_new_protections(template.get("protections", []))

    for user in template.get("users", []):
        create_user(
            name=user["name"],
            email=user["email"],
            full_name=user.get("full_name", ""),
            job_view=user.get("job_view", ""),
            auth_method=user.get("auth_method", ""),
            reviews=user.get("reviews", ""),
        )

    for depot in template.get("depots", []):
        create_depot(
            depot_name=depot["name"],
            depot_type=depot.get("type", "stream"),
            stream_depth=depot.get("depth", "1"),
            user_name=depot.get("user", os.getenv("P4USER")),
        )

    for group in template.get("groups", []):
        create_group(
            group_name=group["name"],
            description=group.get("description", "Autogenerated template group"),
            max_results=group.get("max_results", "unset"),
            max_scan_rows=group.get("max_scan_rows", "unset"),
            max_lock_time=group.get("max_lock_time", "unset"),
            max_open_files=group.get("max_open_files", "unset"),
            timeout=group.get("timeout", "43200"),
            password_timeout=group.get("password_timeout", "unset"),
            subgroups=group.get("subgroups", ""),
            owners=group.get("owners", ""),
            users=group.get("users", ""),
        )

    for stream in template.get("streams", []):
        create_stream(
            depot_name=stream["depot"],
            stream_name=stream["name"],
            stream_type=stream.get("type", "mainline"),
            user_name=stream.get("user", os.getenv("P4USER")),
            parent_view=stream.get("view", "inherit"),
            parent_stream=stream.get("parent", "none"),
            options=stream.get("options"),
            paths=stream.get("paths", ["share ..."]),
            remapped=stream.get("remapped", ""),
            ignored=stream.get("ignored", ""),
        )

    for branch in template.get("branches", []):
        create_branch(
            branch_name=branch["name"],
            view=branch["view"],
            options=branch.get("options", ["unlocked"]),
            owner=branch.get("owner", os.getenv("P4USER")),
        )

        populate_branch(branch["name"])

        delete_branch(branch["name"])


def get_template_preset(preset_name, template_lut_path="preset_templates.json"):
    template_lut = {}

    if os.path.isfile(template_lut_path):
        template_lut = read_json(template_lut_path)

    return template_lut.get(parsed_args.name, "")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--template", default="")
    parser.add_argument("-n", "--name", default="")
    parser.add_argument("-p", "--parameters", nargs='*', default="")

    parsed_args = parser.parse_args()

    script_dir = os.path.dirname(__file__)
    os.chdir(script_dir)

    if parsed_args.template:
        template_filename = parsed_args.template
    elif parsed_args.name:
        template_filename = get_template_preset(parsed_args.name)
    else:
        template_filename = ""

    if template_filename and os.path.isfile(template_filename):
        template = read_json(template_filename)
    
    given_parameters = {}
    if parsed_args.parameters:
        for pairing in parsed_args.parameters:
            key, value = pairing.split(':')
            given_parameters[key] = value

    needed_parameters = gather_parameters(template)

    if not needed_parameters.issubset(set(given_parameters.keys())):
        print(
            'Could not proceed. Not all needed parameters for the provided template have given values.', 
            'The missing parameter keys are:\n',
        )
        [print(_) for _ in needed_parameters if _ not in given_parameters.keys()]
    else:
        template = substitute_parameters(template, given_parameters)
        print('Processing template:', template_filename)
        print(given_parameters)
        process_template(template)