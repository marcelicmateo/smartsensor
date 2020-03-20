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

if exists("/sys/firmware/devicetree/base/model"):
    import adc_daq
else:
    import simulation_adc_daq as adc_daq


# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__)
app.config["suppress_callback_exceptions"] = False
server = app.server

LISTA_MJERENIH_PODATAKA = [
    "Timestamp",
    "Napon NTC",
    "std NTC",
    "Napon SHUNT",
    "std SHUNT",
    "Omjer napona sr. vr.",
    "std Omjera ntc/shunt",
    "Napon NTC [V]",
    "std NTC[V]",
    "Napon SHUNT[V]",
    "std SHUNT [V]",
    "Otpor",
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


def generate_output_table(log, velicina):
    global index_log
    l = df([log])
    print(index_log)
    l.to_csv(LOG_DAT, mode="a", sep=";", index=False, header=False)
    index_log = index_log + 1
    LOG_MJERENJA[index_log] = log
    return [
        LOG_MJERENJA.get(i, {}) for i in list(range(index_log - velicina, index_log, 1))
    ]


with open("config.yaml") as f:
    config = yaml.safe_load(f)


def generate_table_from_dict(dic):
    return [html.Tr(html.Td("{} : {}".format(col[0], col[1]))) for col in dic.items()]


def get_adc_raw_values(sps="ADS1256_3750SPS", number_of_samples=100):
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
        if isinstance(dic, dict):
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
                    value=config.get("resistor").get("resistance"),
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
                    value=config.get("resistor").get("tolerance"),
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
                    value=config.get("resistor").get("betta"),
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
                    value=config.get("resistor").get("bettaTolerance"),
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
                html.H2("Vrijednosti mejernog kruga"),
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
                                html.Td(config.get("resistor").get("resistance")),
                                html.Td(config.get("resistor").get("tolerance")),
                                html.Td(config.get("resistor").get("betta")),
                                html.Td(config.get("resistor").get("bettaTolerance")),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Td("Shunt"),
                                html.Td(config.get("shunt").get("resistance")),
                                html.Td(config.get("shunt").get("tolerance")),
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
                    options=generate_dropdown_dictionary_VALUE_EQ_KEYS(
                        config.get("adc").get("sps_zeff")
                    ),
                    value=list(config.get("adc").get("sps_zeff").keys())[0],
                    clearable=False,
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
                "Koliko mjerenja prema intervalu (sekundi)",
                dcc.Input(
                    id="input_interval_number",
                    value=0,
                    type="number",
                    step=1,
                    min=1,
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
                    min=1,
                    max=500,
                    inputMode="numeric",
                    required=True,
                    disabled=False,
                ),
                html.Button(id="interval-button", n_clicks=0, children="set interval"),
            ]
        ),
        html.Button(id="start-button", disabled=False, n_clicks=0, children="start"),
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
            columns=[{"name": i, "id": i} for i in LISTA_MJERENIH_PODATAKA],
        ),
    ]


app.layout = html.Div(
    children=[
        html.H1("Wellkome"),
        dcc.Interval(
            id="interval_uzoraka",
            interval=2 * 1000,  # in milliseconds 5 min
            n_intervals=0,
            max_intervals=0,
        ),
        dcc.Tabs(
            id="tabs",
            children=[
                dcc.Tab(
                    label="Mjerni krug", children=tab1_mejerne_komponente()
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


# graf raw values of ntc and shunt
@app.callback(
    [Output("output-state", "figure"), Output("table_calculated_values", "data")],
    [Input("start-button", "n_clicks"), Input("interval_uzoraka", "n_intervals")],
    [
        State("number_of_samples", "value"),
        State("sps", "value"),
        State("input_velicina_tablice", "value"),
    ],
)
def update_output(n_clicks, n_intervals, number_of_samples, sps, velicina):
    if number_of_samples is None or n_intervals == 0 and n_clicks == 0:
        raise PreventUpdate

    k = get_adc_raw_values(number_of_samples=number_of_samples, sps=sps)
    i = obrada(
        config={"resistor": config.get("resistor"), "shunt": config.get("shunt")},
        kanali=k,
        zeff=config.get("adc").get("sps_zeff").get(sps),
    )
    return (
        {
            "data": [
                {"y": divide(k[0], numpy.max(k[0])), "name": "raw NTC voltage"},
                {"y": divide(k[1], numpy.max(k[1])), "name": "raw shunt voltage"},
            ],
            "layout": {
                "title": "Raw voltage values",
                "xaxis": {"title": "number of samples taken"},
                "yaxis": {"title": "voltage [V], in raw integer values"},
            },
        },
        generate_output_table(i, velicina),
    )


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
    config["resistor"]["resistance"] = ntc
    config["resistor"]["tolerance"] = tolerancija
    config["resistor"]["betta"] = betta
    config["resistor"]["bettaTolerance"] = btolerancija
    return [generate_table_from_yaml(config)]


if __name__ == "__main__":
    # print(adc_daq.adc_daq(100,'ADS1256_3750SPS'))
    app.run_server(debug=True)
