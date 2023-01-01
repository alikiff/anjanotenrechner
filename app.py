"""Notenrechner-App für Anja"""
from typing import List, Tuple
from dash import Dash, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table

MAX_PUNKTE_DEFAULT = 44

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# Notentabelle bauen
df = pd.DataFrame(
    {
        "Note": ["sehr gut ", "gut ", "befriedigend ", "ausreichend ", "mangelhaft ", "ungenügend "],
        "Prozent": ["87-100", "73-86", "59-72", "45-58", "18-44", "0-17"],
        "Punkte": ["1", "2", "3", "4", "5", "6"],
        "Punkte-gerundet": ["1", "2", "3", "4", "5", "6"]
    }
)

table = dash_table.DataTable(
    id='noten_table',
    columns=[
        {"name": col, "id": col} for col in df.columns
    ],
    data=df.to_dict(orient="records"), editable=True,
    style_table={"width": "600px"}, style_cell={"padding-right": "3px"},
    style_data_conditional=[
        {"if": {"column_id": "Prozent"}, "color": "#009b31"}
    ]
)

#############################################################################################
# Layout bauen
app.layout = html.Div([
    html.H2('Notenrechner'),
    html.Div(id="max_punkte", children=[
        dbc.Label("Maximale Punktanzahl: "),
        dbc.Input("max_punkte_input", type="number", placeholder=MAX_PUNKTE_DEFAULT, value=MAX_PUNKTE_DEFAULT,
                  style={"width": 200, "margin-bottom": "25px"})
    ], ),
    html.Div(children=[
        dbc.Label("Notentabelle: "),
        table

    ])
], style={"margin-left": "20px"})


@app.callback(Output('noten_table', 'data'),
              Input('noten_table', 'data'), Input("max_punkte_input", "value"))
def update_punkte(noten_data, max_punkte):
    """Notentabelle updaten"""
    # Max-Punkte einlesen
    if not isinstance(max_punkte, (float, int)):
        return noten_data

    # Schleife über alle Noten-Reihen
    punkte_lst: List[Tuple] = []
    for row_index, row in enumerate(noten_data):
        if row["Prozent"] is None or len(row["Prozent"].split("-")) != 2:
            return noten_data
        try:
            proz_min = int(row["Prozent"].split("-")[0]) / 100.00
            proz_max = int(row["Prozent"].split("-")[1]) / 100.00
        except ValueError:
            return noten_data
        punkte_min = proz_min * max_punkte
        punkte_max = proz_max * max_punkte
        punkte_lst.append((punkte_min, punkte_max))
        punkte_min_f = str(round(punkte_min, 1)).replace('.', ',')
        punkte_max_f = str(round(punkte_max, 1)).replace('.', ',')
        row["Punkte"] = f"{punkte_min_f} - {punkte_max_f}"

    # Anschließend Berechnen der gerundeten Punkte
    punkte_gerundet_lst: List[Tuple] = []
    for row_index, row in enumerate(noten_data):
        # Für die erste Reihe einfach runden der Punkte
        if row_index == 0:
            punkte_gerund_min = int(round(punkte_lst[row_index][0], 0))
            punkte_gerund_max = int(round(punkte_lst[row_index][1], 0))
        # Für die weiteren Reihen: Max-Wert = Min-Wert der Vorreihe - 1 / Min-Wert wieder gerundet
        else:
            punkte_gerund_min = int(round(punkte_lst[row_index][0], 0))
            punkte_gerund_max = int(punkte_gerundet_lst[row_index - 1][0] - 1)

        row["Punkte-gerundet"] = f"{punkte_gerund_min} - {punkte_gerund_max}"
        punkte_gerundet_lst.append((punkte_gerund_min, punkte_gerund_max))
    return noten_data


if __name__ == '__main__':
    app.run_server(debug=True)
