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
    config = yaml.safe_load(f)


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


def generate_button_inputs():
    return [
        html.Label(
            [
                "NTC RESISTANCE",
                dcc.Input(
                    id="input_ntc_resistance",
                    value=config.get("database").get("ntcresistor").get("resistance"),
                    type="number",
                    step=1,
                    min=1,
                    max=50000,
                    inputMode="numeric",
                    required=True,
                ),
            ]
        ),
        html.Label(
            [
                "NTC TOLERANCE",
                dcc.Input(
                    id="input_ntc_resistance_tolerance",
                    value=config.get("database").get("ntcresistor").get("tolerance"),
                    type="number",
                    step=1,
                    min=1,
                    max=50000,
                    inputMode="numeric",
                    required=True,
                ),
            ]
        ),
        html.Label(
            [
                "NTC BETTA",
                dcc.Input(
                    id="input_ntc_betta",
                    value=config.get("database").get("ntcresistor").get("betta"),
                    type="number",
                    step=1,
                    min=1,
                    max=50000,
                    inputMode="numeric",
                    required=True,
                ),
            ]
        ),
        html.Label(
            [
                "NTC BETTA TOLERANCE",
                dcc.Input(
                    id="input_ntc_betta_tolerance",
                    value=config.get("database")
                    .get("ntcresistor")
                    .get("bettaTolerance"),
                    type="number",
                    step=1,
                    min=1,
                    max=50000,
                    inputMode="numeric",
                    required=True,
                ),
            ]
        ),
        html.Button(id="save_button", n_clicks=0, children="SAVE"),
    ]


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
                                children=[generate_table_from_yaml(config)],
                            )
                        ),
                        dbc.Col(
                            html.Div(
                                style={
                                    "display": "inline-block",
                                    "padding-left": "4rem",
                                },
                                children=generate_button_inputs(),
                            )
                        ),
                    ]
                ),
            ],
        )
    ]


def tab1_mejerne_komponente():
    return [
        html.Div(
            children=[
                html.H6("Demonstraing remote control"),
                dbc.Row(
                    children=[
                        dbc.Col(html.H4("Working configuration")),
                        dbc.Col(html.Button("Change working configuration")),
                    ]
                ),
                html.Table(
                    id="default_values_resistance",
                    children=[
                        html.Thead(
                            html.Tr(
                                [
                                    html.Td(" "),
                                    html.Td(u"Otpror [\u03A9]"),
                                    html.Td("tolerancija [%]"),
                                    html.Td("Betta faktor [K]"),
                                    html.Td("Betta Tolerancija [%]"),
                                ]
                            )
                        ),
                        html.Tr(
                            [
                                html.Td("Ntc"),
                                html.Td(
                                    config.get("database")
                                    .get("ntcresistor")
                                    .get("resistance")
                                ),
                                html.Td(
                                    config.get("database")
                                    .get("ntcresistor")
                                    .get("tolerance")
                                ),
                                html.Td(
                                    config.get("database")
                                    .get("ntcresistor")
                                    .get("betta")
                                ),
                                html.Td(
                                    config.get("database")
                                    .get("ntcresistor")
                                    .get("bettaTolerance")
                                ),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Td("Shunt"),
                                html.Td(
                                    config.get("database")
                                    .get("shunt")
                                    .get("resistance")
                                ),
                                html.Td(
                                    config.get("database").get("shunt").get("tolerance")
                                ),
                            ]
                        ),
                    ],
                ),
                html.Table(
                    id="napajanje",
                    children=[html.Tr([html.Td("Napajanje kruga"), html.Td("3.3 V")])],
                ),
            ]
        ),  # end div with tables
        html.Label(
            [
                "Sampling speed of adc",
                dcc.Dropdown(
                    id="sps",
                    options=[
                        {"label": i, "value": i}
                        for i in config.get("database").get("adc").get("samplingSpeed")
                    ],
                    value=config.get("database").get("adc").get("samplingSpeed")[0],
                    clearable=False,
                    searchable=False,
                ),
            ]
        ),
        html.Label(
            [
                "numbers of samples to take",
                dcc.Input(
                    id="number_of_samples",
                    value=100,
                    type="number",
                    step=1,
                    min=1,
                    max=50000,
                    debounce=True,
                    inputMode="numeric",
                    required=True,
                ),
            ]
        ),
        html.Label(
            [
                "Koliko mjerenja(1. kucica) prema intervalu (2 kucica, sekundi) ",
                dcc.Input(
                    id="input_interval_number",
                    value=0,
                    type="number",
                    step=1,
                    min=0,
                    max=500,
                    inputMode="numeric",
                    required=True,
                    disabled=False,
                ),
                dcc.Input(
                    id="input_interval_time",
                    value=0,
                    type="number",
                    step=1,
                    min=0,
                    max=500,
                    inputMode="numeric",
                    required=True,
                    disabled=False,
                ),
                html.Button(id="interval-button", n_clicks=0, children="set interval"),
                html.Textarea(
                    "prva kucica oznacava broj mjerenja koja ce se napraviti \na druga kucica koliki je interval izmedju 2 uzastopna mjerenja \nkada zavrse sva mjerenja pritisni STOP gumb, (fix this later)"
                ),
            ],
            style={"display": "grid"},
        ),
        html.Button(
            id="start-button",
            disabled=False,
            n_clicks=0,
            children="START jedno mjerenje",
        ),
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
        html.H1("Wellkome"),
        html.H3(
            "Koncept of Smart sensor based on temperature measurement with NTC resistor"
        ),
        dcc.Interval(
            id="interval_uzoraka",
            interval=2 * 1000,  # in milliseconds 5 min
            n_intervals=0,
            max_intervals=0,
        ),
        html.Pre(id="kek"),
        dcc.Tabs(
            id="tabs",
            children=[
                dcc.Tab(
                    label="User Dashboard", children=tab1_mejerne_komponente()
                ),  # end tab 1
                dcc.Tab(
                    label="vrijednosti komponenti", children=tab2_tablica_komponenti()
                ),  # end tab 2
                dcc.Tab(
                    label="obradjeni podaci", children=tab3_povratne_vrijednosti_kruga()
                ),  # end tab 3
            ],
        ),
    ]
)


@app.callback(
    [
        Output("interval_uzoraka", "interval"),
        Output("interval_uzoraka", "max_intervals"),
        Output("interval_uzoraka", "n_intervals"),
        Output("start-button", "disabled"),
        Output("interval-button", "children"),
        Output("input_interval_number", "disabled"),
        Output("number_of_samples", "disabled"),
        Output("sps", "disabled"),
        Output("input_interval_time", "disabled"),
    ],
    [Input("interval-button", "n_clicks")],
    [
        State("start-button", "disabled"),
        State("input_interval_time", "value"),
        State("input_interval_number", "value"),
    ],
)
def periodic_update_toogle(n, disable, interval_time, value):
    if n == 0 or value is None:
        raise PreventUpdate
    return (
        interval_time * 1000,
        (value, 0)[n % 2 == 0],
        (1, 0)[n % 2 == 0],
        not disable,
        ("Set interval", "STOP")[not disable],
        not disable,
        not disable,
        not disable,
        not disable,
    )


# channels=[[],[]]
# graf raw values of ntc and shunt
@app.callback(
    [Output("trigger_adc_got_values", "children")],
    [Input("start-button", "n_clicks"), Input("interval_uzoraka", "n_intervals")],
    [State("number_of_samples", "value"), State("sps", "value"),],
)
def get_adc_values_calculate_stuff(n_clicks, n_intervals, number_of_samples, sps):
    # print(n_clicks, n_intervals)
    # print(number_of_samples is None or n_intervals == 0 and n_clicks == 0)
    if number_of_samples is None or n_intervals == 0 and n_clicks == 0:
        raise PreventUpdate

    channels = get_adc_raw_values(number_of_samples=number_of_samples, sps=sps)

    global index_log
    index_log = index_log + 1

    l = obrada(
        config={
            "ntcresistor": config.get("database").get("ntcresistor"),
            "shunt": config.get("database").get("shunt"),
        },
        kanali=channels,
        zeff=config.get("database").get("adc").get("sps_zeff").get(sps),
    )
    log = {"N": index_log}
    log.update(l)
    df([log]).to_csv(LOG_DAT, mode="a", sep=";", index=False, header=False)

    LOG_MJERENJA[index_log] = log

    return (True,)


@app.callback(
    [Output("save_button", "disabled")],
    [
        Input("input_ntc_betta", "value"),
        Input("input_ntc_resistance", "value"),
        Input("input_ntc_resistance_tolerance", "value"),
        Input("input_ntc_betta_tolerance", "value"),
    ],
)
def save_button_disable_enable(*args):
    """Disables 'SAVE' button if invalid input
    
    Returns:
        Bool -- diables or enables button
    """
    return ([False], [True])[None in args]


@app.callback(
    [Output("component_table", "children")],
    [Input("save_button", "n_clicks")],
    [
        State("input_ntc_resistance", "value"),
        State("input_ntc_resistance_tolerance", "value"),
        State("input_ntc_betta", "value"),
        State("input_ntc_betta_tolerance", "value"),
    ],
)
def update_table(n_clicks, ntc, tolerancija, betta, btolerancija):
    """Update table with new values
    Values are selected by user and only updated 
    when "SAVE" button is presed/activated.
    
    
    Arguments:
        n_clicks {int} -- Triger for save function
        ntc {int} -- new value of NTC resistor
        tolerancija {int} -- value of NTC resistor tolerance in %
        betta {int} -- new value of NTC betta factor
        btolerancija {int} -- new tolerance of betta [%]
    
    Returns:
        Html.Table -- generated html table element
    """
    config["database"]["ntcresistor"]["resistance"] = ntc
    config["database"]["ntcresistor"]["tolerance"] = tolerancija
    config["database"]["ntcresistor"]["betta"] = betta
    config["database"]["ntcresistor"]["bettaTolerance"] = btolerancija
    return [generate_table_from_yaml(config)]


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
