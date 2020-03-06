import yaml
import dash_html_components as html

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
    return html_table_return

print(generate_table(config))