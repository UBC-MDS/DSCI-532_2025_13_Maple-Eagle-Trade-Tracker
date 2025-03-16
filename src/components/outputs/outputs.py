from dash import html
import dash_bootstrap_components as dbc
import altair as alt
import dash_vega_components as dvc
import geopandas as gpd
from data.data import get_agg_geom_data
import numpy as np
import pandas as pd

def create_net_trade_lineplot(df):
    
    df_annual = df.groupby('YEAR').agg({'NET_TRADE': 'sum'}).reset_index()
    df_annual["NET_TRADE"] = df_annual["NET_TRADE"] / 1_000_000  

    chart = (
        alt.Chart(df_annual)
        .mark_line(point=True)
        .encode(
            x=alt.X("YEAR:O", title="Year"),
            y=alt.Y("NET_TRADE:Q", title="Net Trade (Million)", axis=alt.Axis(format="~s")),  
            tooltip=[
                alt.Tooltip("YEAR", title="Year"),
                alt.Tooltip("NET_TRADE", title="Net Trade (M)", format=".2f")  
            ]
        )
        .properties(
            title="Aggregate Net Trade by Year",
            width=320,
            height=80
        )
        .configure_axis(grid=True)
        .interactive()
    )

    return chart.to_dict()


def create_total_trade_card(df, trade_flow):
    df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
    max_year = max(df['YEAR'])

    sum_by_trade_df = df[df['YEAR'] == max_year]

    if np.maximum(np.sum(sum_by_trade_df.get("IMPORT", 0)),np.sum(sum_by_trade_df.get("EXPORT", 0))) > 999_999_999_999:
        if trade_flow.lower() == 'import':
            total_trade_value = np.sum(sum_by_trade_df.get("IMPORT", 0))
            total_trade_value = f"${round(total_trade_value / 1000_000_000_000, 2)}T"
            title = "Total Import Value in CAD by Trillions"
            text_color = 'red'
        else: 
            total_trade_value = np.sum(sum_by_trade_df.get("EXPORT", 0))
            total_trade_value = f"${round(total_trade_value / 1000_000_000_000, 2)}T"
            title = "Total Export Value in CAD by Trillions"
            text_color = 'green'
    elif np.maximum(np.sum(sum_by_trade_df.get("IMPORT", 0)),np.sum(sum_by_trade_df.get("EXPORT", 0))) > 999_999_999:
        if trade_flow.lower() == 'import':
            total_trade_value = np.sum(sum_by_trade_df.get("IMPORT", 0))
            total_trade_value = f"${round(total_trade_value / 1000_000_000, 2)}B"
            title = "Total Import Value in CAD in  Billions"
            text_color = 'red'
        else: 
            total_trade_value = np.sum(sum_by_trade_df.get("EXPORT", 0))
            total_trade_value = f"${round(total_trade_value / 1000_000_000, 2)}B"
            title = "Total Export Value in CAD in Billions"
            text_color = 'green'
    elif np.maximum(np.sum(sum_by_trade_df.get("IMPORT", 0)),np.sum(sum_by_trade_df.get("EXPORT", 0))) > 999_999:
        if trade_flow.lower() == 'import':
            total_trade_value = np.sum(sum_by_trade_df.get("IMPORT", 0))
            total_trade_value = f"${round(total_trade_value / 1000_000, 2)}M"
            title = "Total Import Value in CAD in Millions"
            text_color = 'red'
        else: 
            total_trade_value = np.sum(sum_by_trade_df.get("EXPORT", 0))
            total_trade_value = f"${round(total_trade_value / 1000_000, 2)}M"
            title = "Total Export Value in CAD in Millions"
            text_color = 'green'
    else:
        if trade_flow.lower() == 'import':
            total_trade_value = np.sum(sum_by_trade_df.get("IMPORT", 0))
            total_trade_value = f"${round(total_trade_value / 1000, 2)}K"
            title = "Total Import Value in CAD in Thousands"
            text_color = 'red'
        else: 
            total_trade_value = np.sum(sum_by_trade_df.get("EXPORT", 0))
            total_trade_value = f"${round(total_trade_value / 1000, 2)}K"
            title = "Total Export Value in CAD in Thousands"
            text_color = 'green'

    card = dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-title", 
                    style={"font-size": "1.2rem", "margin-bottom": "0.2rem"}),  
            html.P(total_trade_value,
                   className="card-text",
                   style={"color": text_color, "font-size": "1rem"}) 
        ]),
        style={"width": "18rem", "height": "6rem"},  
    )

    return card


def create_historical_chart(filtered_df, title, trade_flow):

    expected_filters = ["import", "export"]
    if trade_flow not in expected_filters:
        raise ValueError(f"Unexpected input for the trade flow. Expected {expected_filters}")

    filter = trade_flow.upper()
    grouped_df = filtered_df.groupby("YEAR", as_index=False).agg({filter: "sum"}) 
    grouped_df[filter] = grouped_df[filter] / 1_000
    
    chart = (
        alt.Chart(grouped_df)
        .mark_bar()
        .encode(
            x=alt.X("YEAR:O", title="Year"),
            y=alt.Y(f"{filter}:Q", title="Value: Million", axis=alt.Axis(format="~s")),
            tooltip=["YEAR", filter]
        )
        .properties(title=title, width=320, height=100)
        .interactive()
    )
    return chart.to_dict()


def create_chart_card(title, chart_id, height="18rem"):
    """Create a chart card with adjustable height"""
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, className="card-title", style={"font-size": "16px", "margin-bottom": "0.1rem"}),
            dvc.Vega(id=chart_id, style={"width": "100%", "height": height}),
        ], style={"padding": "0.2rem"}),
        className="mb-2",
        style={"width": "100%", "height": height, "padding": "0.1rem"}
    )

def create_chart_card_trend_line(title, chart_id, height="12rem", width="100%"):
    """Create a standardized small Card for Vega charts"""
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, className="card-title", style={"font-size": "0.9rem", "margin-bottom": "0.2rem"}),
            dvc.Vega(id=chart_id, style={"width": width, "height": height})
        ], style={"padding": "0.2rem"}),
        className="mb-1",
        style={"width": "100%", "height": height, "padding": "0.2rem"}
    )

def create_control_card(title, component_id, component, height="30rem"):
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, className="card-title", style={"font-size": "18px"}),
            component
        ]),
        className="mb-2",
        style={"width": "80%", "height": height, "padding": "0.5rem"}
    )