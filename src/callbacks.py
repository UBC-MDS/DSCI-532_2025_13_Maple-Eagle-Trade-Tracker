from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import altair as alt
import dash_vega_components as dvc
import geopandas as gpd
from data.data import clean_data
from data.map_data import (
    get_processed_data, 
    get_agg_geom_data)
from components.inputs.inputs import (
    province_options,
    sector_options,
    province_checklist,
    sector_options,
    sector_checklist)
from components.outputs.outputs import(
    create_net_trade_lineplot,
    create_total_trade_card,
    create_historical_chart,
    create_chart_card,
    create_chart_card_trend_line,
    create_control_card
)
from components.outputs.create_map import get_map_chart
from cache import cache


df = clean_data()
processed_df = get_processed_data() 


@callback(
    [Output("import_card", "children"),
     Output("export_card", "children")],
    [Input("province-dropdown", "value"),
     Input("sector-dropdown", "value")]
)
@cache.memoize()
def update_total_trade_card(selected_provinces, selected_sectors):
    filtered_df = df.copy()

    if "All" not in selected_provinces:
        filtered_df = filtered_df[filtered_df["PROVINCE"].isin(selected_provinces)]
    if "All" not in selected_sectors:
        filtered_df = filtered_df[filtered_df["SECTOR"].isin(selected_sectors)]

    import_card_body = create_total_trade_card(filtered_df, "import").children  
    export_card_body = create_total_trade_card(filtered_df, "export").children  

    return import_card_body, export_card_body

@callback(
    Output("trade_balance_chart", "spec"),
    [Input("province-dropdown", "value"),
     Input("sector-dropdown", "value")]
)

@cache.memoize()
def update_net_trade_lineplot(selected_provinces, selected_sectors):
    filtered_df = df.copy()

    if "All" not in selected_provinces:
        filtered_df = filtered_df[filtered_df["PROVINCE"].isin(selected_provinces)]
    if "All" not in selected_sectors:
        filtered_df = filtered_df[filtered_df["SECTOR"].isin(selected_sectors)]

    net_trade_lineplot = create_net_trade_lineplot(filtered_df)
    return net_trade_lineplot

@callback(
    Output('bar1', 'spec'),
    Input('province-dropdown', 'value')
)
@cache.memoize()
def create_chart(province):
    if "All" in province:
        province = df['PROVINCE'].unique()
    return(
        alt.Chart(df[(df['YEAR'] == 2024) & (df['TRADE_FLOW'] == 'Domestic export') & df['PROVINCE'].isin(province)]).mark_bar().encode(
        x=alt.X('sum(FULL_VALUE)', title='Value'),
        y=alt.Y('SECTOR', title='Sector', axis=alt.Axis(labelLimit=400, titlePadding=80)).sort('-x'),
        tooltip=[
                alt.Tooltip('SECTOR', title='Sector:'),  
                alt.Tooltip('sum(FULL_VALUE)', title='Total export value:', format=',')  
            ]
        ).properties(
            width=260,
            height=120,
            title='Exports to the US in 2024 by sector'
        ).to_dict()
    )

@callback(
    Output('bar2', 'spec'),
    Input('province-dropdown', 'value')
)
@cache.memoize()
def create_chart(province):
    if "All" in province:
        province = df['PROVINCE'].unique()
    return(
        alt.Chart(df[(df['YEAR'] == 2024) & (df['TRADE_FLOW'] == 'Import') & df['PROVINCE'].isin(province)]).mark_bar().encode(
        x=alt.X('sum(FULL_VALUE)', title='Value'),
        y=alt.Y('SECTOR', title='Sector', axis=alt.Axis(labelLimit=400, titlePadding=80)).sort('-x'),
        tooltip=[
                alt.Tooltip('SECTOR', title='Sector:'),  
                alt.Tooltip('sum(FULL_VALUE)', title='Total import value:', format=',') 
            ]
        ).properties(
            width=260,
            height=120,
            title='Imports from the US in 2024 by sector'
        ).to_dict()
    )

@callback(
    Output("trade_geographical_map", "spec"),
    [Input("province-dropdown", "value"),
     Input("sector-dropdown", "value")]
)
@cache.memoize()
def update_map_chart(selected_province, selected_sector):
    """Updates the trade map based on user selections"""
    
    filtered_df = processed_df

    if selected_sector and (isinstance(selected_sector, list) and selected_sector != ['All']):
        filtered_df = filtered_df[filtered_df["SECTOR"].isin(selected_sector)]

    updated_chart = get_map_chart(filtered_df, selected_province)

    return updated_chart.to_dict(format="vega")

@callback(
    [Output("historical_import_chart", "spec"),
     Output("historical_export_chart", "spec")],
    [Input("province-dropdown", "value"),
     Input("sector-dropdown", "value")]
)
@cache.memoize()
def update_historical_charts(selected_provinces, selected_sectors):
    """Update the historical import and export charts based on dropdown selections."""

    filtered_df = df.copy()

    if "All" not in selected_provinces:
        filtered_df = filtered_df[filtered_df["PROVINCE"].isin(selected_provinces)]

    if "All" not in selected_sectors:
        filtered_df = filtered_df[filtered_df["SECTOR"].isin(selected_sectors)]

    import_chart = create_historical_chart(filtered_df[filtered_df["TRADE_FLOW"] == "Import"], "Annual Import")
    export_chart = create_historical_chart(filtered_df[filtered_df["TRADE_FLOW"] == "Domestic export"], "Annual Export")

    return import_chart, export_chart