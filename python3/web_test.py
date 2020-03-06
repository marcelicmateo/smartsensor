import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import yaml


app = dash.Dash(__name__)


with open('/home/mateo/smartsensor/python3/config.yaml') as f:
    config=yaml.safe_load(f)


#generate table from dict format KEY : ITEM
def generate_table(dic):
    html_table_return=[]
    for k,v in dic.items():
        if type(v) is dict:
            html_table_return.append(html.Tr([html.Td("{}".format(k)),generate_table(v)]))
        else:
            html_table_return.append(html.Tr([html.Td("{}".format(k)), html.Td("{}".format(v))]))
    return html.Table(html_table_return)



def tab2_tablica_komponenti(config):
    return [
    dcc.Markdown('''
    ## Vrijednosti elemenata mjernog kruga
    BLA BLA BLA, jebene tablice
    '''),
    generate_table(config)
    ]

app.layout=html.Div(children=
    tab2_tablica_komponenti(config)
)


if __name__ == '__main__':
    #print(adc_daq.adc_daq(100,'ADS1256_3750SPS'))
    app.run_server(debug=True)