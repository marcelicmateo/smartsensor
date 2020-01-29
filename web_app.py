#!/usr/bin python3

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table


app = dash.Dash(__name__)
server = app.server

app.layout=html.Div(children=[
    html.H1('Wellkome'),
    html.Div(children=[
        html.H2('Vrijednosti mejernog kruga'),
        dash_table.DataTable(
            id='tablica_vrijednosti',
            data={
                "NTC otpor" : 22000,
                "Shunt otpor" : 10000,
                "Napon napajanja": 3.3
            }
        )
    ])    
])


if __name__ == '__main__':
    app.run_server(debug=True)