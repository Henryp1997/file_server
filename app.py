import os
import dash
from dash import html, dcc, ctx, no_update as nop
from dash.dependencies import Input, Output, State, ALL
import yaml

# Custom imports
import helper

app = dash.Dash(__name__)
server = app.server  # for hosting

# Load project dicts
here = os.path.dirname(os.path.realpath(__file__))
with open(f"{here}/projects.yaml", "r") as f:
    projects = yaml.safe_load(f)

with open(f"{here}/old_projects.yaml", "r") as f:
    old_projects = yaml.safe_load(f)

app.layout = html.Div([
    # Top banner
    html.Div(
        html.H1(
            "GitLab File Server",
            className="title",
        ),
        style={
            "background-color": "#FFE0E0",
            "border-radius": "8px",
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "border": "2px solid #AAAAAA"
        }
    ),

    # Project lists, file tree etc
    html.Div([
        html.Div(
            html.A(
                "GitLab Projects",
                id="header",
                className="header header_not_clickable",
            ),
            style={"padding-top": "1.5vh"}
        ),
        html.Div([
            html.Ul(
                [html.Li(
                    html.A(
                        f"\u2192 {project}",
                        id={"type": "project_link", "name": project, "path": path},
                        className="htmlA_clickable",
                        style={"font-size": "30px"},
                        n_clicks=0
                    ),
                    style={"margin-bottom": "1.5vh"}
                )
                for project, path in projects.items()
                ], 
                id={"type": "project_list", "name": "projects"},
                style={"listStyleType": "none", "display": "block"}
            )
        ]),
        html.Div(
            html.A(
                "Deprecated Projects",
                id="deprecated_header",
                className="header header_not_clickable"
            ),
            style={"padding-top": "1.5vh"}
        ),
        html.Div([
            html.Ul(
                [html.Li(
                    html.A(
                        f"\u2192 {project}",
                        id={"type": "project_link", "name": project, "path": path},
                        className="htmlA_clickable",
                        style={"font-size": "30px"},
                        n_clicks=0
                    ),
                    style={"margin-bottom": "1.5vh"}
                )
                for project, path in old_projects.items()
                ], 
                id={"type": "project_list", "name": "old_projects"},
                style={"listStyleType": "none", "display": "block"}
            )
        ]),
        dcc.Store(id="current_project_path", data=None),
        dcc.Store(id="opened_folders", data=[]),
        dcc.Download(id="download_component"),
        html.Ul(id="file_tree", style={"display": "none"})
    ], style={
        "background-color": "#F2F2FD",
        "min-height": "100vh",
        "margin-top": "1.5vh",
        "border": "2px solid #AAAAAA",
        "border-radius": "8px"
    })
])


### CALLBACKS
@app.callback(
    Output("download_component", "data"),
    Input(
        {"type": "tree-item", "item_type": "file", "name": ALL, "path": ALL},
        "n_clicks"
    ),
    prevent_initial_call=True
)
def download_file(n_clicks_list):
    """ Download selected file """
    triggered = ctx.triggered_id
    path = triggered["path"]

    if all(val == 0 for val in n_clicks_list):
        return

    return dcc.send_file(path)


@app.callback(
    Output("file_tree", "style", True),
    Output(
        {"type": "project_list", "name": ALL},
        "style",
        True
    ),
    Output("header", "children", True),
    Output("header", "className", True),
    Output("deprecated_header", "style", True),
    Output("current_project_path", "data"),
    Input(
        {"type": "project_link", "name": ALL, "path": ALL},
        "n_clicks"
    ),
    prevent_initial_call=True
)
def choose_project(_):   
    """ 
    Handle user clicking project name. Hide project
    lists and show contents of clicked project
    """
    project = ctx.triggered_id
    new_header = f"{project['name']} (click here to go back to projects)"
    new_header_class = "header header_clickable"
    return (
        helper.block,
        [helper.hide, helper.hide],
        new_header,
        new_header_class,
        helper.hide,
        project["path"]
    )
    

@app.callback(
    Output("file_tree", "style", True),
    Output(
        {"type": "project_list", "name": ALL},
        "style",
        True
    ),
    Output("header", "children", True),
    Output("header", "className", True),
    Output("deprecated_header", "style", True),
    Output("current_project_path", "data", True),
    Output("opened_folders", "data", True),
    Input("header", "n_clicks"),
    State("header", "children"),
    prevent_initial_call=True
)
def navigate_with_header(n, header_text):
    """
    Re-show project lists and hide current project
    contents if header clicked. Reset opened_folders list
    """
    if "(click here to go back to projects)" in header_text:
        new_header_class = "header header_not_clickable"
        list_style = {"listStyleType": "none", "display": "block"}
        return (
            helper.hide,
            [list_style, list_style],
            "GitLab Projects",
            new_header_class,
            helper.show,
            None,
            []
        )
    return (nop,)*6


@app.callback(
    Output("file_tree", "children"),
    Input("opened_folders", "data"),
    Input("current_project_path", "data"),
    State("file_tree", "style"),
)
def update_tree(opened, path, tree_style):
    """ Update directory tree with contents of project """
    if tree_style["display"] != "none":
        file_tree = helper.populate_file_tree(path, opened)
        return file_tree
    return ""


@app.callback(
    Output("opened_folders", "data"),
    Input({"type": "tree-item", "item_type": "dir", "name": ALL, "path": ALL}, "n_clicks"),
    State("opened_folders", "data"),
    prevent_initial_call=True
)
def toggle_folder(n_clicks_list, opened):
    """ Show contents of the clicked directory, hide if clicked again """
    triggered = ctx.triggered_id

    if all(n_clicks == 0 for n_clicks in n_clicks_list):
        return opened
    
    path = triggered["path"]
    if path in opened:
        opened.remove(path)
    else:
        opened.append(path)
    return opened


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
