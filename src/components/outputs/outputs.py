from dash import html
import dash_bootstrap_components as dbc
import altair as alt
import dash_vega_components as dvc
import geopandas as gpd
from data.map_data import get_agg_geom_data

def create_net_trade_lineplot(df):
    reshaped_df = df.pivot(index=['YEAR_MONTH', 'YEAR', 'PROVINCE', 'SECTOR'],
                           columns='TRADE_FLOW', 
                           values='FULL_VALUE').reset_index()

    reshaped_df['NET'] = reshaped_df['Domestic export'] - reshaped_df['Import']
    df_annual = reshaped_df.groupby(['YEAR', 'PROVINCE', 'SECTOR']).agg({'NET': 'sum'}).reset_index()
    df_annual = df_annual.groupby('YEAR').agg({'NET': 'sum'}).reset_index()

    df_annual["NET"] = df_annual["NET"] / 1_000_000  

    chart = (
        alt.Chart(df_annual)
        .mark_line(point=True)
        .encode(
            x=alt.X("YEAR:O", title="Year"),
            y=alt.Y("NET:Q", title="Net Trade (Million)", axis=alt.Axis(format="~s")),  
            tooltip=[
                alt.Tooltip("YEAR", title="Year"),
                alt.Tooltip("NET", title="Net Trade (M)", format=".2f")  
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
    max_year = max(df['YEAR'])

    sum_by_trade_df = df[df['YEAR'] == max_year].groupby('TRADE_FLOW')['VALUE'].sum()

    if trade_flow.lower() == 'import':
        total_trade_value = sum_by_trade_df.get("Import", 0) / 1_000_000 
        title = "Total Import Value in CAD (Million)"
        text_color = 'red'
    else:
        total_trade_value = sum_by_trade_df.get("Domestic export", 0) / 1_000_000
        title = "Total Export Value in CAD (Million)"
        text_color = 'green'

    card = dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-title", 
                    style={"font-size": "1.2rem", "margin-bottom": "0.2rem"}),  
            html.P(f"${total_trade_value:,.2f}",
                   className="card-text",
                   style={"color": text_color, "font-size": "1rem"}) 
        ]),
        style={"width": "18rem", "height": "6rem"},  
    )

    return card


def create_historical_chart(filtered_df, title):
    grouped_df = filtered_df.groupby("YEAR", as_index=False).agg({"VALUE": "sum"}) 
    grouped_df["VALUE"] = grouped_df["VALUE"] / 1_000
    
    chart = (
        alt.Chart(grouped_df)
        .mark_bar()
        .encode(
            x=alt.X("YEAR:O", title="Year"),
            y=alt.Y("VALUE:Q", title="Value: Million", axis=alt.Axis(format="~s")),
            tooltip=["YEAR", "VALUE"]
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