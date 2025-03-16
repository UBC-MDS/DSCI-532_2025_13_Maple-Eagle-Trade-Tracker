from dash import html
import dash_bootstrap_components as dbc
import altair as alt
import dash_vega_components as dvc
import geopandas as gpd
from data.data import get_agg_geom_data
import numpy as np
import pandas as pd

import altair as alt
import pandas as pd

def create_net_trade_lineplot(df):
    df_annual = df.groupby('YEAR').agg({'NET_TRADE': 'sum'}).reset_index()
    
    max_trade = abs(df_annual["NET_TRADE"]).max()

    if max_trade >= 1_000_000_000_000:
        scale_factor, unit, format_unit = 1_000_000_000_000, "Trillion", "T"
    elif max_trade >= 1_000_000_000:
        scale_factor, unit, format_unit = 1_000_000_000, "Billion", "B"
    elif max_trade >= 1_000_000:
        scale_factor, unit, format_unit = 1_000_000, "Million", "M"
    elif max_trade >= 1_000:
        scale_factor, unit, format_unit = 1_000, "Thousand", "K"
    else:
        scale_factor, unit, format_unit = 1, "", ""

    df_annual["NET_TRADE"] = df_annual["NET_TRADE"] / scale_factor

    line = (
        alt.Chart(df_annual)
        .mark_line(color="gray") 
        .encode(
            x=alt.X("YEAR:O", title="Year"),
            y=alt.Y("NET_TRADE:Q", title=f"Net Trade ({unit})", axis=alt.Axis(format="~s"))
        )
    )

    points = (
        alt.Chart(df_annual)
        .mark_point(size=20)  
        .encode(
            x="YEAR:O",
            y="NET_TRADE:Q",
            color=alt.condition(
                alt.datum.NET_TRADE > 0,
                alt.value("green"),  
                alt.value("red")  
            ),
            tooltip=[
                alt.Tooltip("YEAR", title="Year"),
                alt.Tooltip("NET_TRADE", title=f"Net Trade ({format_unit})", format=".2f")
            ]
        )
    )

    chart = (
        (line + points) 
        .properties(title="Aggregate Net Trade by Year", width=320, height=80)
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
    if trade_flow.lower() not in expected_filters:
        raise ValueError(f"Unexpected input for the trade flow. Expected {expected_filters}")

    trade_col = trade_flow.upper() 
    grouped_df = filtered_df.groupby("YEAR", as_index=False).agg({trade_col: "sum"})
    max_value = grouped_df[trade_col].max()
    min_value = grouped_df[trade_col].min()

    if max_value >= 1_000_000_000_000:
        scale_factor, unit, format_unit = 1_000_000_000_000, "Trillion", "T"
    elif max_value >= 1_000_000_000:
        scale_factor, unit, format_unit = 1_000_000_000, "Billion", "B"
    elif max_value >= 1_000_000:
        scale_factor, unit, format_unit = 1_000_000, "Million", "M"
    elif max_value >= 1_000:
        scale_factor, unit, format_unit = 1_000, "Thousand", "K"
    else:
        scale_factor, unit, format_unit = 1, "", ""

    grouped_df[trade_col] = grouped_df[trade_col] / scale_factor

    color_scale = alt.Scale(
        domain=[min_value / scale_factor, max_value / scale_factor],  
        range=["yellow", "red"] if trade_flow.lower() == "import" else ["yellow", "green"]
    )

    chart = (
        alt.Chart(grouped_df)
        .mark_bar()
        .encode(
            x=alt.X("YEAR:O", title="Year"),
            y=alt.Y(
                f"{trade_col}:Q",
                title=f"Value ({unit})",
                axis=alt.Axis(format="~s")
            ),
            color=alt.Color(
                f"{trade_col}:Q",
                scale=color_scale,
                legend=None  
            ),
            tooltip=[
                alt.Tooltip("YEAR", title="Year"),
                alt.Tooltip(trade_col, title=f"Value ({format_unit})", format=".2f")
            ]
        )
        .properties(
            title=title,
            width=320,
            height=100
        )
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