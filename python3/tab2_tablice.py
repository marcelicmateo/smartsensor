import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import yaml
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate


app = dash.Dash(__name__)


with open("/home/mateo/smartsensor/python3/config.yaml") as f:
    config = yaml.safe_load(f)


# generate table from yaml dictionary
def generate_table(dic):
    html_table_return = []
    for k, v in dic.items():
        if type(v) is dict:
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
                        generate_table(v),
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
                    debounce=True,
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
                    debounce=True,
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
                    debounce=True,
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
                    debounce=True,
                    inputMode="numeric",
                    required=True,
                ),
            ]
        ),
        html.Button(id="save_button", n_clicks=0, children="SAVE"),
    ]


def tab2_tablica_komponenti():
    return [
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
                        children=[generate_table(config)],
                    )
                ),
                dbc.Col(
                    html.Div(
                        style={"display": "inline-block", "padding-left": "4rem"},
                        children=generate_button_inputs(),
                    )
                ),
            ]
        ),
    ]


app.layout = html.Div(
    style={"display": "inline-block"}, children=tab2_tablica_komponenti()
)


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
def update_output(n_clicks, *args):
    if n_clicks == 0:
        raise PreventUpdate
    config["resistor"]["resistance"] = args[0]
    config["resistor"]["tolerance"] = args[1]
    config["resistor"]["betta"] = args[2]
    config["resistor"]["bettaTolerance"] = args[3]
    return [generate_table(config)]


if __name__ == "__main__":
    # print(adc_daq.adc_daq(100,'ADS1256_3750SPS'))
    app.run_server(debug=True)
