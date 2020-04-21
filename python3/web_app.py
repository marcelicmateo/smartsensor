import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import yaml
from obrada import obrada
from numpy import divide, recarray
import numpy
import json
import dash_bootstrap_components as dbc
from pandas import DataFrame as df
from pandas import read_csv
from os.path import exists
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import database_create
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import text


engine = database_create.main()

if exists("/sys/firmware/devicetree/base/model"):
    import adc_daq
else:
    import simulation_adc_daq as adc_daq


app = dash.Dash(__name__)
app.config["suppress_callback_exceptions"] = False
app.title = "PYpi"
server = app.server


LISTA_MJERENIH_PODATAKA = [
    "N",
    "Timestamp",
    "Napon NTC",
    "Napon std NTC",
    "Napon SHUNT",
    "std SHUNT",
    "Omjer napona sr. vr.",
    "std Omjera ntc/shunt",
    "Napon NTC [V]",
    "std NTC[V]",
    "Napon SHUNT[V]",
    "std SHUNT [V]",
    "Otpor",
    "otpor std NTC",
    "Utjecaj tolerancije shunta",
    "Temperatura izracunata polinomom",
    "STD Temperature polinomom",
    "Temperatura izracunata exp.",
    "STD temperature Exp.",
    "Vrijeme obrade",
]

LOG_DAT = "log_mjerenja6.csv"

if not exists(LOG_DAT):
    df(columns=LISTA_MJERENIH_PODATAKA).to_csv(LOG_DAT, index=False, sep=";")
    index_log = 0
    LOG_MJERENJA = {}
else:
    LOG_MJERENJA = read_csv(LOG_DAT, sep=";").to_dict("index")
    index_log = len(LOG_MJERENJA) - 1


with open("config.yaml") as f:
    def_config = yaml.safe_load(f)


def generate_table_from_dict(dic):
    return [html.Tr(html.Td("{} : {}".format(col[0], col[1]))) for col in dic.items()]


def get_adc_raw_values(sps="ADS1256_3750SPS", number_of_samples=100):
    """Function to get adc raw values
    
    Keyword Arguments:
        sps {str} -- string describing sample speed of adc
        must be of format 'ADS1256_{sps}SPS' (default: {"ADS1256_3750SPS"})
        number_of_samples {int} -- number of consecutive samples to take per one channel of adc  (default: {100})
    
    Returns:
        numpy.array(dtype=int32) -- dimensions [2][number_of_samples]
    """
    return adc_daq.adc_daq(number_of_samples=number_of_samples, sps=sps)


def generate_dropdown_dictionary_VALUE_EQ_KEYS(dictionary):
    drop = []
    for key in dictionary.keys():
        drop.append({"label": key, "value": key})
    return drop


def dict_to_markdown(dict):
    c = json.dumps(dict)
    return c


# generate table from yaml dictionary
def generate_table_from_yaml(dic):
    html_table_return = []
    for k, v in dic.items():
        if isinstance(v, dict):
            html_table_return.append(
                html.Tr(
                    [
                        html.Td(
                            style={
                                "font-weight": "bold",
                                "border-right": "double",
                                "vertical-align": "top",
                            },
                            children="{}".format(k),
                        ),
                        generate_table_from_yaml(v),
                    ]
                )
            )
        else:
            html_table_return.append(
                html.Tr(
                    [
                        html.Td(style={"font-weight": "bold"}, children="{}".format(k)),
                        html.Td("{}".format(v)),
                    ]
                )
            )
    return html.Table(html_table_return)


def tab2_tablica_komponenti():
    return [
        html.Div(
            style={"display": "inline-block"},
            children=[
                dcc.Markdown(
                    """
                    ## Vrijednosti elemenata mjernog kruga
                    BLA BLA BLA, jebene tablice
                    """
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                id="component_table",
                                style={"display": "inline-block"},
                                children=[generate_table_from_yaml(def_config)],
                            )
                        ),
                    ]
                ),
            ],
        )
    ]


from sqlalchemy.orm import relationship, sessionmaker


def make_tables_from_active_conf_in_database(engine):
    table_list = []
    global config
    connection = engine.connect()
    t = text(
        "SELECT ntcresistor, shunt, powerSuply, adc, refVoltage, numberofsamples, samplingspeed, period FROM activeconfiguration"
    )
    result = connection.execute(t).fetchall()
    config = {
        "period": result[-1][7],
        "number_of_samples": result[-1][5],
        "sps": result[-1][6],
    }
    table_one = dash_table.DataTable(
        id="table_active_conf",
        merge_duplicate_headers=True,
        columns=[
            {"id": "1", "name": "Active configuration"},
            {"id": "2", "name": "Active configuration"},
            {"id": "3", "name": "Active configuration"},
            {"id": "4", "name": "Active configuration"},
        ],
        data=[
            {
                "1": "Resistor",
                "2": result[-1][0],
                "3": "Number of samples",
                "4": result[-1][5],
            },
            {
                "1": "Shunt",
                "2": result[-1][1],
                "3": "Sampling speed",
                "4": result[-1][6],
            },
            {"1": "Power Suply", "2": result[-1][2], "3": "Period", "4": result[-1][7]},
            {"1": "ADC", "2": result[-1][3]},
            {"1": "Referent voltage", "2": result[-1][4]},
        ],
        style_table={"padding-right": "0.1em", "padding-down": "0.5em"},
    )
    t = text("SELECT id,resistance,tolerance,betta,bettaTolerance FROM  ntcresistor")
    result = connection.execute(t).fetchall()
    config["ntcresistance"] = result[-1][1]
    config["ntctolerance"] = result[-1][2]
    config["betta"] = result[-1][3]
    config["bettatolerance"] = result[-1][4]

    table_two = dash_table.DataTable(
        id="table_ntcresistor",
        merge_duplicate_headers=True,
        columns=[
            {"id": "1", "name": "NTC RESISTOR"},
            {"id": "2", "name": "NTC RESISTOR"},
        ],
        data=[
            {"1": "id", "2": result[-1][0]},
            {"1": "resistance", "2": result[-1][1]},
            {"1": "tolerance", "2": result[-1][2]},
            {"1": "betta", "2": result[-1][3]},
            {"1": "betta Tolerance", "2": result[-1][4]},
        ],
        style_table={"padding-right": "0.1em"},
    )
    t = text("SELECT id,resistance,tolerance FROM  shunt")
    result = connection.execute(t).fetchall()
    config["shuntresistance"] = result[-1][1]
    config["shunttolerance"] = result[-1][2]
    table_three = dash_table.DataTable(
        id="table_shunt",
        merge_duplicate_headers=True,
        columns=[{"id": "1", "name": "Shunt"}, {"id": "2", "name": "Shunt"},],
        data=[
            {"1": "id", "2": result[-1][0]},
            {"1": "resistance []", "2": result[-1][1]},
            {"1": "tolerance [%]", "2": result[-1][2]},
        ],
        style_table={"padding-right": "0.1em"},
    )
    t = text("SELECT id, voltage, settlingtime FROM  powersuply")
    result = connection.execute(t).fetchall()
    table_four = dash_table.DataTable(
        id="table_powersuply",
        merge_duplicate_headers=True,
        columns=[{"id": "1", "name": "Power"}, {"id": "2", "name": "Power"},],
        data=[
            {"1": "id", "2": result[-1][0]},
            {"1": "Voltage [V]", "2": result[-1][1]},
            {"1": "Settling Time [s]", "2": result[-1][2]},
        ],
        style_table={"padding-right": "0.1em"},
    )
    t = text("SELECT id, samplingspeed, impedance, clockFreq FROM  adc")
    result = connection.execute(t).fetchall()
    config["zeff"] = result[-1][2].split(",")[0]
    table_five = dash_table.DataTable(
        id="table_adc",
        merge_duplicate_headers=True,
        columns=[{"id": "1", "name": "ADC"}, {"id": "2", "name": "ADC"},],
        data=[
            {"1": "id", "2": result[-1][0]},
            {"1": "sampling Speed", "2": result[-1][1].split(",")[0], "id": "sps"},
            {"1": "impedance", "2": result[-1][2].split(",")[0], "id": "zeff"},
            {"1": "clockFreq", "2": result[-1][3]},
        ],
        style_table={"padding-right": "0.1em"},
    )
    t = text("SELECT id, voltage FROM  refVoltage")
    result = connection.execute(t).fetchall()
    table_six = dash_table.DataTable(
        id="table_six",
        merge_duplicate_headers=True,
        columns=[
            {"id": "1", "name": "Referent Voltage"},
            {"id": "2", "name": "Referent Voltage"},
        ],
        data=[
            {"1": "id", "2": result[-1][0]},
            {"1": "Voltage [V]", "2": result[-1][1]},
        ],
        style_table={"padding-right": "0.1em"},
    )
    return (
        dbc.Row(dbc.Col(table_one)),
        dbc.Row(html.Button("Open details", id="collapse-button")),
        html.Div(
            children=[
                dbc.Row(
                    children=[
                        dbc.Col(table_two),
                        dbc.Col(table_three),
                        dbc.Col(table_four),
                        dbc.Col(table_five),
                        dbc.Col(table_six),
                    ],
                )
            ],
            id="collapse",
            className="colapse_div",
            hidden=True,
            style={},
        ),
    )


def user_dashboard():
    return [
        html.Div(
            children=[
                html.H6(
                    "Demonstraing remote control and user Dashboard for given sensor"
                ),
                dbc.Row(
                    children=[
                        dbc.Col(html.H4("Working configuration")),
                        dbc.Col(html.Button("Change working configuration")),
                    ],
                    style={"justify-content": "space-between"},
                ),
                dbc.Row(
                    children=html.Div(make_tables_from_active_conf_in_database(engine))
                ),
            ]
        ),  # end div with tables
        dcc.Graph(id="output-state"),
    ]


def tab3_povratne_vrijednosti_kruga():
    return [
        html.Label(
            [
                "Velicina tablice",
                dcc.Input(
                    id="input_velicina_tablice",
                    value=5,
                    type="number",
                    step=1,
                    min=1,
                    max=10,
                    inputMode="numeric",
                    required=True,
                ),
            ]
        ),
        dash_table.DataTable(
            id="table_calculated_values",
            columns=[
                {"name": i, "id": i, "selectable": True}
                for i in (LISTA_MJERENIH_PODATAKA)
            ],
            editable=True,
            row_selectable="single",
            column_selectable="multi",
        ),
        html.Div(id="output_display_selected_data"),
        dcc.Graph(id="output_display_column"),
    ]


app.layout = html.Div(
    children=[
        html.Div(id="trigger_adc_got_values", style={"visibility": "hidden",}),
        html.H1("Welcome"),
        html.H3(
            "Concept of Smart sensor based on temperature measurement with NTC resistor"
        ),
        html.Pre(id="kek"),
        dcc.Tabs(
            id="tabs",
            children=[
                dcc.Tab(label="User Dashboard", children=user_dashboard()),  # end tab 1
                dcc.Tab(
                    label="vrijednosti komponenti", children=tab2_tablica_komponenti()
                ),  # end tab 2
                dcc.Tab(
                    label="obradjeni podaci", children=tab3_povratne_vrijednosti_kruga()
                ),  # end tab 3
            ],
        ),
        dcc.Interval(
            id="interval_uzoraka",
            interval=config.get("period") * 1000,  # in milliseconds 5 min
            n_intervals=0,
            max_intervals=-1,
        ),
    ]
)


@app.callback(
    Output("collapse", "hidden"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "hidden")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# channels=[[],[]]
# graf raw values of ntc and shunt
@app.callback(
    [Output("trigger_adc_got_values", "children")],
    [Input("interval_uzoraka", "n_intervals")],
)
def get_adc_values_calculate_stuff(n_intervals):
    # print(n_clicks, n_intervals)
    # print(number_of_samples is None or n_intervals == 0 and n_clicks == 0)
    # if n_intervals == 0:
    #   raise PreventUpdate
    print(n_intervals)
    channels = get_adc_raw_values(
        number_of_samples=config.get("number_of_samples"), sps=config.get("sps")
    )

    global index_log
    index_log = index_log + 1

    l = obrada(config, kanali=channels, zeff=int(config.get("zeff")))
    log = {"N": index_log}
    log.update(l)
    df([log]).to_csv(LOG_DAT, mode="a", sep=";", index=False, header=False)

    LOG_MJERENJA[index_log] = log

    return (True,)


import plotly.express as px


@app.callback(
    [Output("output-state", "figure")], [Input("trigger_adc_got_values", "children")]
)
def graf_temperature(triger):
    # fig = go.Figure()
    l = {}
    velicina = 100
    for i in list(range(index_log - velicina + 1, index_log + 1, 1)):
        d = LOG_MJERENJA.get(i, {})
        l[i] = d
    # print(l)
    fig = px.line(
        df(l).transpose(),
        x="Timestamp",
        y="Temperatura izracunata polinomom",
        title="Temperatura",
    )
    # LOG_MJERENJA[index_log]
    return [fig]


@app.callback(
    Output("table_calculated_values", "data"),
    [
        Input("trigger_adc_got_values", "children"),
        Input("input_velicina_tablice", "value"),
    ],
)
def generate_output_table(triger, velicina):
    l = []
    for i in list(range(index_log - velicina + 1, index_log + 1, 1)):
        d = LOG_MJERENJA.get(i, {})
        d.update({"N": i})
        l.append(d)
    return l


@app.callback(
    Output("output_display_selected_data", "children"),
    [
        Input("table_calculated_values", "derived_viewport_data"),
        Input("table_calculated_values", "derived_viewport_selected_rows"),
    ],
)
def prikaz_pojedinog_mjerenja_iz_tablice(K, V):
    if K is None or V is None or V == []:
        raise PreventUpdate
    return generate_table_from_yaml(K[V[0]])


@app.callback(
    Output("output_display_column", "figure"),
    [
        Input("table_calculated_values", "derived_viewport_selected_columns"),
        Input("table_calculated_values", "derived_viewport_data"),
    ],
)
def graf_selected_columns(sel, data):
    if data is None or sel is None or sel == []:
        raise PreventUpdate
    data2 = df(data)
    fig = go.Figure()
    x_axis = list(data2.get("Timestamp"))
    for s in sel:
        fig.add_trace(go.Scatter(x=x_axis, y=list(data2.get(s))))
    return fig


if __name__ == "__main__":
    # print(adc_daq.adc_daq(100,'ADS1256_3750SPS'))
    app.run_server(debug=True)
