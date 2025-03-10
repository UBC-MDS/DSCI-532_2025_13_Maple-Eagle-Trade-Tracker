from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import altair as alt
import dash_vega_components as dvc
import geopandas as gpd
import callbacks
from data import df
from components.inputs import (
    province_options,
    sector_options,
    province_checklist,
    sector_options,
    sector_checklist)
from components.outputs import(
    create_net_trade_lineplot,
    create_total_trade_card,
    create_historical_chart,
    get_agg_geom_data,
    get_map_chart,
    create_chart_card,
    create_chart_card_trend_line,
    create_control_card
)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Br(),
            create_control_card("Select Province/Territory", "province-dropdown", province_checklist, height="21.5rem"),
            create_control_card("Select Trade Sector", "sector-dropdown", sector_checklist, height="32rem")
        ], width=2, style={"padding": "0.2rem", "margin-right": "-3rem", "margin-top": "-0.8rem"}), 

        dbc.Col([
            dbc.Row([
                dbc.Card(
                dbc.CardBody([
                    html.H4("Maple Eagle Trade Tracker", className="text-center")
                ]), style={"width": "20%", "height": "7.1rem", "margin-top": "1rem", "margin-left": "0.8rem"}  
            ),
                dbc.Col(dbc.Card(id="import_card", style={"width": "18rem", "padding": "0.2rem"}), width=3, style={"margin-left": "0rem", "margin-top": "1rem"}), 
                dbc.Col(dbc.Card(id="export_card", style={"width": "18rem", "padding": "0.2rem"}), width=3, style={"margin-left": "-2.5rem", "margin-top": "1rem"}),
                dbc.Col(create_chart_card_trend_line("Trade Balance Over Time", "trade_balance_chart"), width=4, style={"margin-left": "-2.7rem", "margin-top": "1rem"})  
            ], className="mb-1"),

            dbc.Row([
                dbc.Col(create_chart_card("Trade Geographical Distribution", "trade_geographical_map", height="32rem"), 
                        width=7, style={"width": "56.5rem", "margin-right": "-0.5rem", "margin-top": "-4rem"}),  
                dbc.Col([
                    dbc.Row([
                        create_chart_card("Annual Import", "historical_import_chart", height="13rem")
                    ], className="mb-1"),
                    dbc.Row([
                        create_chart_card("Annual Export", "historical_export_chart", height="13rem")
                    ], className="mb-1")
                ], width=3, style={'flex': '0 0 32%', "margin-left": "1rem", "margin-top": "1rem"})
            ], className="mb-1"),

            dbc.Row([
                dbc.Col(create_chart_card("Imports from the US in 2024 by Sector", "bar2", height="13rem"), width=6, style={"width": "42.8rem"}),
                dbc.Col(create_chart_card("Exports to the US in 2024 by Sector", "bar1", height="13rem"), width=6, style={"width": "42.8rem"})
            ], className="mb-1"),
        ], width=10, style={"margin-left": "-0.5rem"}) 
    ], className="mb-1"),

    dbc.Row([
        dbc.Col([
            html.P(
                "Developed by Sopuruchi Chisom (@cs-uche), Bryan Lee (@BryanLee06), Alex Wong (@awlh18), and Yun Zhou (@Green-zy), "
                "this dashboard provides an interactive visualization of Canada's 2014 - 2024 trade metrics, helping policymakers identify "
                "the most affected sectors and regions to support informed decision-making on economic policies. View the project on GitHub:",
                className="small text-muted mb-1",
                style={"max-width": "100%", "margin-top": "0px"}
            ),
            html.A(
                "UBC-MDS/DSCI-532_2025_13_Maple-Eagle-Trade-Tracker",
                href="https://github.com/UBC-MDS/DSCI-532_2025_13_Maple-Eagle-Trade-Tracker",
                target="_blank",
                className="small text-primary"
            )
        ], width=8, className="text-left mt-0")
    ], className="mt-0 mb-0")

], fluid=True)


if __name__ == '__main__':
    app.server.run(port=8000, host='127.0.0.1')
