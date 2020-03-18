"""
A simple app demonstrating how to dynamically render tab content containing
dcc.Graph components to ensure graphs get sized correctly. We also show how
dcc.Store can be used to cache the results of an expensive graph generation
process so that switching tabs is fast.
"""
import time

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout =html.Div(children=[ html.Label(['Koliko mjerenja prema intervalu od 5 min',
                dcc.Input(
                        id='input_interval_number'
                        ,value = 0
                        ,type = 'number'
                        ,step = 1
                        ,min = 1
                        ,max = 500
                        ,inputMode = "numeric"
                        ,required=True
                        ,disabled=False
                    )
            ,html.Button(id='interval-button', n_clicks=0, children="set interval")
            ])
            ,html.Button(id='start-button', disabled=False, n_clicks=0, children="start")
            ,dcc.Interval(
            id='interval_uzoraka',
            interval=5*60*1000, # in milliseconds 5 min
            n_intervals=0,
            max_intervals=0
            )
])

@app.callback([Output('interval_uzoraka', 'max_intervals')
                , Output('start-button', 'disabled')
                , Output('interval-button', 'children')
                , Output('input_interval_number', 'disabled')]
                , [Input('interval-button', 'n_clicks')]
                , [State('start-button', 'disabled')
                , State('input_interval_number', 'value')]
            )
def periodic_update_enable(n, disable, value):
    if n == 0:
        raise PreventUpdate
    print('UPDATE')
    return value, not disable, ('Set interval', "STOP")[not disable], not disable



if __name__ == "__main__":
    app.run_server(debug=True, port=8888)