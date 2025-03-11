from dash import html
import dash_bootstrap_components as dbc
import altair as alt
import dash_vega_components as dvc
import geopandas as gpd
import numpy as np

def create_net_trade_lineplot(df):
    
    # reshaped_df = df.pivot(index=['YEAR_MONTH', 'YEAR', 'PROVINCE', 'SECTOR'],
    #                        columns='TRADE_FLOW', 
    #                        values='FULL_VALUE').reset_index()

    # reshaped_df['NET'] = reshaped_df['Domestic export'] - reshaped_df['Import']
    # df_annual = reshaped_df.groupby(['YEAR', 'PROVINCE', 'SECTOR']).agg({'NET': 'sum'}).reset_index()
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
    max_year = max(df['YEAR'])

    sum_by_trade_df = df[df['YEAR'] == max_year]

    if trade_flow.lower() == 'import':
        total_trade_value = np.sum(sum_by_trade_df.get("IMPORT", 0)) / 1_000_000 
        title = "Total Import Value in CAD (Million)"
        text_color = 'red'
    else:
        total_trade_value = np.sum(sum_by_trade_df.get("EXPORT", 0)) / 1_000_000
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

def get_agg_geom_data(df):
    """Aggregate the geometric data using processed_df"""
    
    url = 'https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip'
    canadian_provinces = gpd.read_file(url).query("iso_a2 == 'CA'")[
        ['name', 'geometry']
    ]
    canadian_provinces.columns = [col.upper() for col in canadian_provinces.columns]

    if 'NET_TRADE' not in df.columns:
        raise KeyError("NET_TRADE column is missing from the processed dataset.")

    aggr_data = df.groupby('PROVINCE')[['NET_TRADE']].sum().reset_index()
    geo_data = aggr_data.merge(canadian_provinces, how='inner', left_on='PROVINCE', right_on='NAME')
    geo_data = geo_data.drop(columns=['NAME'])
    geo_data = gpd.GeoDataFrame(geo_data, geometry='GEOMETRY')

    return geo_data


def get_map_chart(df, selected_province):
    """Returns a geographical map chart object"""

    aggr_data = get_agg_geom_data(df)
    aggr_data["NET_TRADE"] = aggr_data["NET_TRADE"] / 1_000_000

    default_color = alt.Color(
        'NET_TRADE:Q', 
        scale=alt.Scale(
            scheme='redyellowgreen',
            domain=[aggr_data["NET_TRADE"].min(), aggr_data["NET_TRADE"].max()],
            nice=False  
        ),
        legend=alt.Legend(
            title="Net Trade (Million CAD)",  
            format="~s",
            orient="right",  
            offset=-75  
        )
    )

    color_encoding = default_color if not selected_province or "All" in selected_province else alt.condition(
        alt.FieldOneOfPredicate(field='PROVINCE', oneOf=selected_province),
        default_color,
        alt.value("#ECECEC")
    )

    hover = alt.selection_point(fields=['PROVINCE'], on='pointerover', empty=False)

    map_chart = alt.Chart(aggr_data, width=800, height=500).mark_geoshape(
        strokeWidth=2
    ).encode(
        tooltip=[
            alt.Tooltip('PROVINCE:N', title="Province"), 
            alt.Tooltip('NET_TRADE:Q', format=".2f", title="Net Trade (Million CAD)")  
        ],
        color=color_encoding, 
        stroke=alt.condition(hover, alt.value('white'), alt.value('#222222')),
        order=alt.condition(hover, alt.value(1), alt.value(0))
    ).properties(
        width=800,
        height=450
    ).configure(
        background='transparent'
    ).project(
        'transverseMercator',
        rotate=[90, 0, 0]
    ).add_params(
        hover
    )

    return map_chart


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