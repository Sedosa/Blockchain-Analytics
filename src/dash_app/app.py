import os, logging
import sqlite3
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd

DB_PATH = os.getenv("DB_PATH","")

con = sqlite3.connect(DB_PATH)

DF = pd.read_sql_query('SELECT * FROM CRYPTO_PRICE',con)
logging.info("Data read from sqlite3 database")
DF['DATE'] = pd.to_datetime(DF['DATE'],unit="s")

logging.info("building dashboard")
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

all_tickers = DF['TICKER'].unique()

app.layout = html.Div([
    dcc.Checklist(
        id="checklist",
        options=[{"label": x, "value": x} 
                 for x in all_tickers],
        value=all_tickers[:6],
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id="line-chart"),
])

@app.callback(
    Output("line-chart", "figure"), 
    [Input("checklist", "value")])
def update_line_chart(tickers):
    mask = DF['TICKER'].isin(tickers)
    fig = px.line(DF[mask], 
                x="DATE", y="VALUE", color='TICKER',
                width=700, height=900,
                title="Portfolio Value by Currency",
                labels={
                    "DATE" : "Date",
                    "VALUE" : "Value (GBP)"
                }
                , template="simple_white")
    fig.update_xaxes(rangeslider_visible=True)
    logging.info("Graph updated")
    return fig
################################
# CALLBACKS
################################

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)s: %(asctime)s] %(filename)s, %(funcName)s, line %(lineno)d : %(message)s"
    )
    app.run_server(debug=True)