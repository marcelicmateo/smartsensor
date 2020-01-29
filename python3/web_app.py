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



app = dash.Dash(__name__)
server = app.server

def generate_table(dic):
    return html.Table(
        [html.Tr(html.Td("{} : {}".format(col[0],col[1]))) for col in dic.items()]    
    )
def get_adc_raw_values(sps='ADS1256_3750SPS', number_of_samples=100):
    return(adc_daq.adc_daq(number_of_samples,sps))



app.layout=html.Div(children=[
    html.H1('Wellkome'),
    html.Div(children=[
        html.H2('Vrijednosti mejernog kruga'),
        generate_table({"otpor" : 22000, "shunt": 10000, "napajanje" : 3.3})
        , html.Button(id='start-button', n_clicks=0, children="start")
        ,dcc.Graph(id='output-state')
        ])
    ])

@app.callback(Output('output-state', 'figure'),
      [Input('start-button', 'n_clicks')])
def update_output(n_clicks):
    if n_clicks==0:
        raise PreventUpdate
    else:
        k=get_adc_raw_values()
        #print(k)
        return {
            'data' : [ {
                'y' : k[0]
                }
                ,{
                'y' : k[1]
                }
            ]
        }
 #   html.Div(children=[
 #       dcc.Graph={id='graf_raw_kanala',
 #       figure={
 #           'data':
 #       }
 #       }


if __name__ == '__main__':
    #print(adc_daq.adc_daq(100,'ADS1256_3750SPS'))
    app.run_server(debug=True)