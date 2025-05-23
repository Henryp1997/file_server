import os
from collections import namedtuple
from pathlib import Path
from dash import html

IconTypes = namedtuple("icons", ("text", "settings", "python", "data", "script", "image"))
icons = IconTypes(
    "\U0001F4C4",
    "\u2699\uFE0F ",
    "\U0001F40D",
    "\U0001F4CA",
    "\U0001F4DD",
    "\U0001F5BC\uFE0F "
)

hide = {"display": "none"}
block = {"display": "block"}
show = {}

def populate_file_tree(dir, opened_paths):
    base = Path(dir)
    root = list(base.glob("*"))
    files = []
    dirs = []
    gitignore_list = get_gitignore_list(base)
    extensions = {
        ".txt"  : icons.text,
        ".yaml" : icons.settings,
        ".json" : icons.settings,
        ".py"   : icons.python,
        ".csv"  : icons.data,
        ".m"    : icons.script,
        ".css"  : icons.script,
        ".cpp"  : icons.script,
        ".png"  : icons.image,
        ".jpg"  : icons.image,
        ".jpeg" : icons.image
    }

    root_files = [i for i in root if not i.is_dir()]
    root_dirs = list(set(root) - set(root_files))

    for file in root_files:
        icon = extensions.get(file.suffix.lower(), extensions[".txt"])
        file_name = file.name

        do_append = check_if_ignored(file_name, "file", gitignore_list)
        if do_append:
            files.append(create_list_item(icon, file_name, item_type="file", path=str(file)))

    # Sort the file list. Priorities python then csv files
    # All other files sorted alphabetically
    files = sorted(files, key=sort_priority)

    # Directories. Must be recursive
    for dir in root_dirs:
        icon = "\U0001F4C1"
        dir_name = dir.name
        path = str(dir)

        do_append = check_if_ignored(dir_name, "dir", gitignore_list)
        if do_append:
            is_open = path in opened_paths
            child_items = populate_file_tree(path, opened_paths) if is_open else []
            dirs.append(
                create_list_item(
                    icon,
                    dir_name,
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


def get_gitignore_list(base):
    """ First check if there is a .gitignore - don't want to show those files/dirs """
    gitignore_list = []
    if os.path.exists(base / ".gitignore"):
        with open(base / ".gitignore", "r") as f:
            gitignore_list = f.readlines()
        gitignore_list = [i.strip("\n") for i in gitignore_list]
    return gitignore_list


def check_if_ignored(name, item_type, gitignore_list):
    """ Check if a file/dir is in .gitignore so we can skip past it in app display """
    do_append = True

    # Check for fullstop in front of file/dir (hidden file/dir)
    if name.startswith("."):
        return False

    for ignore in gitignore_list:
        if name == ignore:
            do_append = False

        if item_type == "file":
            if ignore == f"*{Path(name).suffix}":
                # E.g., if *.csv in .gitignore, all .csv files are ignored
                return False

    return do_append


def sort_priority(file_component: html.Li):
    # First child is html.A, second is html.A text contents
    filename = Path(file_component.children[0].children)
    name = filename.name
    ext = filename.suffix

    if ext == ".py": group = 0
    elif ext == ".m": group = 1
    elif ext == ".csv": group = 2
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
