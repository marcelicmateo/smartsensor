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
from numpy import divide, max
import json

#external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


app = dash.Dash(__name__)
server = app.server

with open('config.yaml') as f:
    config=yaml.safe_load(f)

#generate table from dict
def generate_table(dic):
    return [html.Tr(html.Td("{} : {}".format(col[0],col[1]))) for col in dic.items()]

def get_adc_raw_values(sps='ADS1256_3750SPS', number_of_samples=100):
    return(adc_daq.adc_daq(number_of_samples=number_of_samples,sps=sps))

def generate_dropdown_dictionary_VALUE_EQ_KEYS(dictionary):
    drop=[]
    for key in dictionary.keys():
        drop.append({'label' : key, 'value' : key})
    return drop

def dict_to_markdown(dict):
    c=json.dumps(dict)
    return  c

app.layout=html.Div(children=[
    html.H1('Wellkome'),
    dcc.Tabs(id='tabs', children=[
        dcc.Tab(label='Mjerni krug', children=[
        html.Div(children=[
            html.H2('Vrijednosti mejernog kruga')
            ,html.Table(id='default_values_resistance',children=[
                html.Thead(html.Tr([
                    html.Td(" ")
                    ,html.Td(u"Otpror [\u03A9]")
                    ,html.Td("tolerancija [%]")
                    ,html.Td("Betta faktor [K]")
                    ,html.Td("Betta Tolerancija [%]")
                ]))
                ,html.Tr([
                    html.Td("Ntc")
                    ,html.Td(config.get('resistor').get('resistance'))
                    ,html.Td(config.get('resistor').get('tolerance'))
                    ,html.Td(config.get('resistor').get('betta'))
                    ,html.Td(config.get('resistor').get('bettaTolerance'))
                    ])
                ,html.Tr([
                    html.Td("Shunt")
                    ,html.Td(config.get('shunt').get('resistance'))
                    ,html.Td(config.get('shunt').get('tolerance'))
                    ])
                ])
            ,html.Table(id='napajanje', children=[
                html.Tr([
                    html.Td("Napajanje kruga")
                    ,html.Td("3.3 V")
                ])
            ])
        ]) #end div with tables
            ,html.Label(['Sampling speed of adc'
                ,dcc.Dropdown(
                    id='sps'
                    ,options = generate_dropdown_dictionary_VALUE_EQ_KEYS(config.get('adc').get('sps_and_zeff'))
                    ,value = list(config.get('adc').get('sps_and_zeff').keys())[0]
                    ,clearable = False
                )])
            ,html.Label(['numbers of samples to take'
                ,dcc.Input(
                    id='number_of_samples'
                    ,value = 100
                    ,type = 'number'
                    ,step = 1
                    ,min = 1
                    ,max = 50000
                    ,debounce = True
                    ,inputMode = "numeric"
                    ,required = True
            )])
            ,html.Button(id='start-button', n_clicks=0, children="start")
            ,dcc.Graph(id='output-state')
            ,html.Table(id='calculated_values')
    ])#end tab 1
    ,dcc.Tab(label='vrijednosti komponenti', children=[
        html.H2('vrijednosti komponeneti koristanih u mjernom lancu')
        ,dcc.Markdown(id='vrijednosti_komponenti'
            ,children=[
                dict_to_markdown(config)
            ])

    ])#end of tab 2

    ])#end tabs
    ], #end 1 div children
    id='raw'
)# end app

# graf raw values of ntc and shunt
@app.callback([Output('output-state', 'figure')
            ,Output('calculated_values', 'children')]
      ,[Input('start-button', 'n_clicks')]
      ,[State('number_of_samples', 'value')
      ,State('sps', 'value')])
def update_output(n_clicks, number_of_samples, sps):
    if n_clicks==0 or number_of_samples is None:
        raise PreventUpdate
    else:
        k=get_adc_raw_values(number_of_samples=number_of_samples, sps=sps)
        #print(k)
        i=obrada(config=config, kanali=k, sps=sps)
        return {
            'data' : [ {
                'y' : divide(k[0], max(k[0])) ,
                'name' : 'raw NTC voltage'
                }
                ,{
                'y' : divide(k[1], max(k[1])),
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