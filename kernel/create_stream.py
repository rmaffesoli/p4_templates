#!/usr/bin/env python

"""create_stream doc string"""

from __future__ import print_function


def create_stream(
    server,
    depot_name=None,
    stream_name=None,
    user_name=None,
    stream_type="mainline",
    parent_view=None,
    parent_stream=None,
    options=None,
    paths=None,
    remapped=None,
    ignored=None,
    dryrun=0,
):
    """create_stream doc string"""

    existing_stream_names = {_["Stream"] for _ in server.iterate_streams()}

    full_streamname = "//{}/{}".format(depot_name, stream_name)

    if full_streamname in existing_stream_names:
        print("Stream {} already exists\n".format(full_streamname))
        return

    if parent_stream and "//" not in parent_stream:
        parent_stream = "/".join(["/", depot_name, parent_stream])

    stream_spec = server.fetch_stream(full_streamname)

    if not options:
        if stream_type in ["mainline", "virtual"]:
            options = "allsubmit unlocked notoparent nofromparent mergedown"
        elif stream_type in ["development", "task"]:
            options = "allsubmit unlocked toparent fromparent mergedown"

    if user_name:
        stream_spec["Owner"] = user_name
    if stream_type:
        stream_spec["Type"] = stream_type
    if parent_view:
        stream_spec["ParentView"] = parent_view
    if parent_stream:
        stream_spec["Parent"] = parent_stream
    if paths:
        stream_spec["Paths"] = paths
    if remapped:
        stream_spec["Remapped"] = remapped
    if ignored:
        stream_spec["Ignored"] = ignored
    if options:
        stream_spec["Options"] = options

    if dryrun:
        print("-" * 20)
        print(stream_spec)
        print("-" * 20)
    elif stream_spec["Type"] == "development" and stream_spec["Parent"] == "none":
        print("Skipping orphaned development stream", full_streamname)
    else:
        result = server.save_stream(stream_spec)
        print(result)
