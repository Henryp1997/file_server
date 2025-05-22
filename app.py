import dash
from dash import html, dcc, ctx
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

app.layout = html.Div([
    html.Div(
        html.H1(
            "GitLab File Server",
            className="title",
        ),
        style={
            "background-color": "#FFE0E0",
            "border-radius": "5px",
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center"
        }
    ),
    html.Div([
        html.A(
            "GitLab Projects",
            id="header",
            className="header_clickable",
        ),
        html.Div([
            html.Ul(
                [html.Li(
                    html.A(
                        project,
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
        dcc.Store(id="current_project_path", data=None),
        dcc.Store(id="opened-folders", data=[]),
        html.Ul(id="file-tree", style={"display": "none"})
    ], style={"background-color": "#F2F2FD"})
])


### CALLBACKS
# @app.server.route("/download/<path:filename>")
# def download_file(filename):
#     return flask.send_from_directory(ROOT_DIR, filename, as_attachment=True)


@app.callback(
    Output("file-tree", "style", allow_duplicate=True),
    Output("project_list", "style", allow_duplicate=True),
    Output("header", "children", allow_duplicate=True),
    Output("current_project_path", "data"),
    Input({"type": "project_link", "name": ALL, "path": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def choose_project(n_clicks_list):   
    project = ctx.triggered_id
    return {"display": "block"}, {"display": "none"}, "File Explorer (click to go back)", project["path"]
    

@app.callback(
    Output("file-tree", "style", allow_duplicate=True),
    Output("project_list", "style", allow_duplicate=True),
    Output("header", "children", allow_duplicate=True),
    Output("current_project_path", "data", allow_duplicate=True),
    Output("opened-folders", "data", allow_duplicate=True),
    Input("header", "n_clicks"),
    State("header", "children"),
    prevent_initial_call=True
)
def navigate_with_header(n, header_text):
    if header_text == "File Explorer (click to go back)":
        return {"display": "none"}, {"listStyleType": "none", "display": "block"}, "GitLab Projects", None, []


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
    app.run_server(debug=True)
