import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
collapse = html.Div(
    [
        dbc.Button(
            "Open collapse", id="collapse-button", className="mb-3", color="primary",
        ),
        dbc.Collapse(html.P("never hide component"), id="collapse",),
    ]
)
app.layout = collapse


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(debug=True)
