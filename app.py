import dash
from dash import html, dcc, ctx, no_update as nop
from dash.dependencies import Input, Output, State, ALL
import yaml
import flask
import os

# Custom imports
import helper

app = dash.Dash(__name__)
server = app.server  # for hosting

with open("projects.yaml", "r") as f:
    projects = yaml.safe_load(f)

with open("old_projects.yaml", "r") as f:
    old_projects = yaml.safe_load(f)

app.layout = html.Div([
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
    html.Div([
        html.Div(
            html.A(
                "GitLab Projects",
                id="header",
                className="header_clickable"
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
                id="project_list",
                style={"listStyleType": "none", "display": "block"}
            )
        ]),
        html.Div(
            html.A(
                "Deprecated Projects",
                id="deprecated_header",
                className="header_clickable"
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
                id="old_project_list",
                style={"listStyleType": "none", "display": "block"}
            )
        ]),
        dcc.Store(id="current_project_path", data=None),
        dcc.Store(id="opened-folders", data=[]),
        dcc.Download(id="download_component"),
        html.Ul(id="file-tree", style={"display": "none"})
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
    Input({"type": "tree-item", "item_type": "file", "name": ALL, "path": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def download_file(n_clicks_list):
    triggered = ctx.triggered_id
    path = triggered["path"]

    if all(val == 0 for val in n_clicks_list):
        return

    return dcc.send_file(path)


@app.callback(
    Output("file-tree", "style", allow_duplicate=True),
    Output("project_list", "style", allow_duplicate=True),
    Output("old_project_list", "style", allow_duplicate=True),
    Output("header", "children", allow_duplicate=True),
    Output("deprecated_header", "style", allow_duplicate=True),
    Output("current_project_path", "data"),
    Input({"type": "project_link", "name": ALL, "path": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def choose_project(n_clicks_list):   
    project = ctx.triggered_id
    hide = {"display": "none"}
    show = {"display": "block"}
    return show, hide, hide, f"{project['name']} (click here to go back to projects)", hide, project["path"]
    

@app.callback(
    Output("file-tree", "style", allow_duplicate=True),
    Output("project_list", "style", allow_duplicate=True),
    Output("old_project_list", "style", allow_duplicate=True),
    Output("header", "children", allow_duplicate=True),
    Output("deprecated_header", "style", allow_duplicate=True),
    Output("current_project_path", "data", allow_duplicate=True),
    Output("opened-folders", "data", allow_duplicate=True),
    Input("header", "n_clicks"),
    State("header", "children"),
    prevent_initial_call=True
)
def navigate_with_header(n, header_text):
    if "(click here to go back to projects)" in header_text:
        list_style = {"listStyleType": "none", "display": "block"}
        return {"display": "none"}, list_style, list_style, "GitLab Projects", {}, None, []
    return (nop,)*6


@app.callback(
    Output("file-tree", "children"),
    Input("opened-folders", "data"),
    Input("current_project_path", "data"),
    State("file-tree", "style"),
)
def update_tree(opened, path, style):
    if style["display"] == "block":
        file_tree = helper.populate_file_tree(path, opened)
        return file_tree
    return ""


@app.callback(
    Output("opened-folders", "data"),
    Input({"type": "tree-item", "item_type": "dir", "name": ALL, "path": ALL}, "n_clicks"),
    State("opened-folders", "data"),
    prevent_initial_call=True
)
def toggle_folder(n_clicks_list, opened):
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
    app.run(debug=True)
