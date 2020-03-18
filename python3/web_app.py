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
import dash_bootstrap_components as dbc

#external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True
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


#generate table from yaml dictionary
def generate_table(dic):
    html_table_return=[]
    for k,v in dic.items():
        if type(v) is dict:
            html_table_return.append(html.Tr([html.Td(style={'font-weight': 'bold', 'border-right' : 'double' ,  'vertical-align' : 'top'},children="{}".format(k)),generate_table(v)]))
        else:
            html_table_return.append(html.Tr([html.Td(style={'font-weight': 'bold'},children="{}".format(k)), html.Td("{}".format(v))]))
    return html.Table(html_table_return)

def generate_button_inputs():
    return [ html.Label(['NTC RESISTANCE',dcc.Input(
                    id='input_ntc_resistance'
                    ,value = config.get('resistor').get('resistance')
                    ,type = 'number'
                    ,step = 1
                    ,min = 1
                    ,max = 50000
                    ,debounce = True
                    ,inputMode = "numeric"
                    ,required = True
            )]) ,html.Label(['NTC TOLERANCE',dcc.Input(
                    id='input_ntc_resistance_tolerance'
                    ,value = config.get('resistor').get('tolerance')
                    ,type = 'number'
                    ,step = 1
                    ,min = 1
                    ,max = 50000
                    ,debounce = True
                    ,inputMode = "numeric"
                    ,required = True
            )])  ,html.Label(['NTC BETTA',dcc.Input(
                    id='input_ntc_betta'
                    ,value = config.get('resistor').get('betta')
                    ,type = 'number'
                    ,step = 1
                    ,min = 1
                    ,max = 50000
                    ,debounce = True
                    ,inputMode = "numeric"
                    ,required = True
            )]) ,html.Label(['NTC BETTA TOLERANCE',dcc.Input(
                    id='input_ntc_betta_tolerance'
                    ,value = config.get('resistor').get('bettaTolerance')
                    ,type = 'number'
                    ,step = 1
                    ,min = 1
                    ,max = 50000
                    ,debounce = True
                    ,inputMode = "numeric"
                    ,required = True
            )]) ,html.Button(id='save_button', n_clicks=0, children="SAVE")
            ]


def tab2_tablica_komponenti():
    return [html.Div(style={'display': 'inline-block'},children=[
    dcc.Markdown('''
    ## Vrijednosti elemenata mjernog kruga
    BLA BLA BLA, jebene tablice
    ''')
    ,dbc.Row([
    dbc.Col(html.Div(id='component_table',style={'display': 'inline-block'},children=[generate_table(config)]))
    ,dbc.Col(html.Div(style={'display': 'inline-block', 'padding-left' : '4rem'},children=generate_button_inputs()))
    ])])]

def tab1_mejerne_komponente():
    return [
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
                    ,options = generate_dropdown_dictionary_VALUE_EQ_KEYS(config.get('adc').get('sps_zeff'))
                    ,value = list(config.get('adc').get('sps_zeff').keys())[0]
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
            ,dcc.Interval(
            id='interval_uzoraka',
            interval=5*60*1000, # in milliseconds 5 min
            n_intervals=0,
            max_intervals=0
            )
            ,html.Label(['Koliko mjerenja prema intervalu od 5 min',
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
            ])
            ,html.Button(id='interval-button', n_clicks=0, children="set interval")
            ,html.Button(id='start-button', disabled=False, n_clicks=0, children="start")
            ,dcc.Graph(id='output-state')
    ]

def tab3_povratne_vrijednosti_kruga():
    return[
        html.Table(id='calculated_values')
    ]
    
    

app.layout=html.Div(children=[
    html.H1('Wellkome'),
    dcc.Tabs(id='tabs', children=[
        dcc.Tab(label='Mjerni krug', children=tab1_mejerne_komponente())                           #end tab 1
        ,dcc.Tab(label='vrijednosti komponenti', children=tab2_tablica_komponenti())    #end tab 2
        ,dcc.Tab(label='obradjeni podaci', children=tab3_povratne_vrijednosti_kruga())])
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

# graf raw values of ntc and shunt
@app.callback([Output('output-state', 'figure')
            ,Output('calculated_values', 'children')]
      ,[Input('start-button', 'n_clicks')
      , Input('interval_uzoraka', 'n_intervals')]
      ,[State('number_of_samples', 'value')
      ,State('sps', 'value')])
def update_output(n_clicks, n_intervals, number_of_samples, sps):
    if n_clicks==0 or number_of_samples is None:
        raise PreventUpdate
    else:
        k=get_adc_raw_values(number_of_samples=number_of_samples, sps=sps)
        #print(k)
        i=obrada(config={'resistor' : config.get('resistor'),'shunt':  config.get('shunt')}
                , kanali=k
                , zeff = config.get('adc').get('sps_zeff').get(sps))
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



@app.callback(  [Output('component_table', 'children') ]
                ,[  Input('save_button', 'n_clicks')]
                ,[  State('input_ntc_resistance' ,'value')
                ,   State('input_ntc_resistance_tolerance', 'value')
                ,   State('input_ntc_betta','value')    
                ,   State('input_ntc_betta_tolerance','value')
                ])
def update_output(n_clicks,*args):
    if n_clicks==0:
        raise PreventUpdate
    config['resistor']['resistance']        =args[0]
    config['resistor']['tolerance']         =args[1]
    config['resistor']['betta']             =args[2]
    config['resistor']['bettaTolerance']    =args[3]
    return [generate_table(config)]



if __name__ == '__main__':
    #print(adc_daq.adc_daq(100,'ADS1256_3750SPS'))
    app.run_server(debug=True)