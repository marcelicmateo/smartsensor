import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import adc_daq
import ADS1256
import config
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import yaml
from obrada import obrada



app = dash.Dash(__name__)
server = app.server

def generate_table(dic):
    return [html.Tr(html.Td("{} : {}".format(col[0],col[1]))) for col in dic.items()]

def get_adc_raw_values(sps='ADS1256_3750SPS', number_of_samples=100):
    return(adc_daq.adc_daq(number_of_samples,sps))



app.layout=html.Div(children=[
    html.H1('Wellkome'),
    html.Div(children=[
            html.H2('Vrijednosti mejernog kruga'),
            html.Table(id='default_values_table',children=generate_table({"otpor" : 22000, "shunt": 10000, "napajanje" : 3.3}))
            ,html.Button(id='start-button', n_clicks=0, children="start")
            ,dcc.Graph(id='output-state')
            ,html.Table(id='calculated_values')
        ], 
        id='raw'
    )
])

@app.callback([Output('output-state', 'figure'),
            Output('calculated_values', 'children')],
      [Input('start-button', 'n_clicks')])
def update_output(n_clicks):
    if n_clicks==0:
        raise PreventUpdate
    else:
        k=get_adc_raw_values()
        #print(k)
        with open('config.yaml') as f:
            config=yaml.safe_load(f)
        i=obrada(config=config, kanali=k)
        return {
            'data' : [ {
                'y' : k[0],
                'name' : 'raw NTC voltage'
                }
                ,{
                'y' : k[1],
                'name' : 'raw shunt voltage'
                }
            ],
            'layout' : {
                'title' : 'Raw voltage values',
                'xaxis' : {'title' : "number of samples taken"},
                'yaxis' : {'title' : "voltage [V], in raw integer values"}
            }
        }, generate_table(i)



if __name__ == '__main__':
    #print(adc_daq.adc_daq(100,'ADS1256_3750SPS'))
    app.run_server(debug=True)