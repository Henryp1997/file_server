import dash
from dash import html, dcc, ctx
from dash.dependencies import Input, Output, State, ALL
import flask
import os

# Custom imports
import helper

app = dash.Dash(__name__)
server = app.server  # for hosting

ROOT_DIR = r"C:\ALL_WORK\code\python-bi"

app.layout = html.Div([
    html.Div(
        html.H1(
            "GitLab File Server",
            className="title",
            style={
                "display": "inline-block",
                "margin-right": "8vw",
                "padding-top": "0",
                "margin-top": "0",
                "padding-left": "0"
            }
        ),
        style={
            "background-color": "#EFEFEF",
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center"
        }
    ),
    html.H3("File Explorer", style={"font-size": "24px", "margin-left": "1.5vw"}),
    dcc.Store(id="opened-folders", data=[]),
    html.Ul(id="file-tree")
])


### CALLBACKS
@app.server.route("/download/<path:filename>")
def download_file(filename):
    return flask.send_from_directory(ROOT_DIR, filename, as_attachment=True)


@app.callback(
    Output("file-tree", "children"),
    Input("opened-folders", "data")
)
def update_tree(opened):
    file_tree = helper.populate_file_tree(ROOT_DIR, opened)
    return file_tree


@app.callback(
    Output("opened-folders", "data"),
    Input({"type": "tree-item", "item_type": "dir", "name": ALL, "path": ALL}, "n_clicks"),
    State("opened-folders", "data"),
    prevent_initial_call=True
)
def toggle_folder(n_clicks, opened):
    triggered = ctx.triggered_id
    path = triggered["path"]
    if path in opened:
        opened.remove(path)
    else:
        opened.append(path)
    return opened


if __name__ == "__main__":
    app.run_server(debug=True)
