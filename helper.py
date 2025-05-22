import os
from pathlib import Path
from dash import html


def populate_file_tree(dir, opened_paths):
    base = Path(dir)
    root = list(base.glob("*"))
    files = []
    dirs = []

    extensions = {
        ".txt" : "\U0001F4C4",
        ".yaml": "\u2699\uFE0F ",
        ".json": "\u2699\uFE0F ",
        ".py"  : "\U0001F40D",
        ".csv" : "\U0001F4CA"
    }

    root_files = [i for i in root if not i.is_dir()]
    root_dirs = list(set(root) - set(root_files))

    for file in root_files:
        icon = extensions.get(file.suffix, extensions[".txt"])
        name = file.name
        files.append(create_list_item(icon, name, item_type="file", path=str(file)))

    # Sort the file list. Priorities python then csv files
    # All other files sorted alphabetically
    files = sorted(files, key=sort_priority)

    # Directories. Must be recursive
    for dir in root_dirs:
        icon = "\U0001F4C1"
        name = dir.name
        path = str(dir)
        is_open = path in opened_paths
        child_items = populate_file_tree(path, opened_paths) if is_open else []
        dirs.append(
            create_list_item(
                icon,
                name,
                item_type="dir",
                path=path,
                child_items=child_items,
                ul_style={
                    "marginLeft": "1em",
                    "display": "block" if is_open else "none"
                }
            )
        )

    return dirs + files


def sort_priority(file_component: html.Li):
    # First child is html.A, second is html.A text contents
    filename = Path(file_component.children[0].children)
    name = filename.name
    ext = filename.suffix
    is_hidden = name.split(" ")[1].startswith(".")

    if ext == ".py": group = 0
    elif ext == ".csv": group = 1
    elif is_hidden: group = 2
    else: group = 3

    return (group, name.lower())


def create_list_item(icon, name, item_type, path, child_items=None, ul_style={"display": "none"}):
    return html.Li([
        html.A(
            f"{icon} {name}",
            className="htmlA_clickable",
            n_clicks=0,
            id={
                "type": "tree-item",
                "item_type": item_type, # "dir" or "file"
                "name": name,
                "path": path
            }
        ),
        html.Ul(
            children=[] if child_items is None else child_items,
            id={
                "type": "tree-content",
                "path": path
            },
            style=ul_style
        ),
    ], className="file_list_item")
