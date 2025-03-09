from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import altair as alt
import dash_vega_components as dvc
import geopandas as gpd

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

df = pd.read_csv('data/clean/clean_data.csv')
processed_df = pd.read_csv('data/clean/processed_data.csv') 

province_options = [{'label': 'All', 'value': 'All'}] + [
    {'label': province, 'value': province} for province in sorted(df['PROVINCE'].dropna().unique())
]

sector_options = [{'label': 'All', 'value': 'All'}] + [
    {'label': sector, 'value': sector} for sector in sorted(df['SECTOR'].dropna().unique())
]

province_options = [
    {'label': province, 'value': province} for province in sorted(df['PROVINCE'].dropna().unique())
]

province_dropdown = dcc.Dropdown(
    id='province-dropdown',
    options=province_options,
    value=[province_options[1]["value"]],
    clearable=False,
    multi=True
)

sector_options = [
    {'label': sector, 'value': sector} for sector in sorted(df['SECTOR'].dropna().unique())
]

sector_checklist = dcc.Checklist(
    id='sector-dropdown',
    options=sector_options,
    value=[sector_options[1]["value"]],  
    inputStyle={"margin-right": "5px", "margin-left": "10px"},  
    labelStyle={
        "display": "block", 
        "margin-left": "20px", 
        "text-indent": "-29px",
        "font-size": "12px" 
    },
    style={"max-width": "180px", "word-wrap": "break-word"}
)


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
    grouped_df["VALUE"] = grouped_df["VALUE"] / 1_000_000
    
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

    default_color = alt.Color(
                        'NET_TRADE:Q', 
                        scale=alt.Scale(scheme='redyellowgreen'),
                        legend=alt.Legend(title="Net Trade")
                    )
    color_encoding = default_color if not selected_province or "All" in selected_province else alt.condition(
        alt.FieldOneOfPredicate(field='PROVINCE', oneOf=selected_province),
        default_color,
        alt.value("#ECECEC" ) 
    )

    hover = alt.selection_point(fields=['PROVINCE'], on='pointerover', empty=False)

    map_chart = alt.Chart(aggr_data, width=700, height=300).mark_geoshape(
        strokeWidth=2
    ).encode(
        tooltip=['PROVINCE:N', alt.Tooltip('NET_TRADE:Q', format=',')],
        color=color_encoding, 
        stroke=alt.condition(hover, alt.value('white'), alt.value('#222222')),
        order=alt.condition(hover, alt.value(1), alt.value(0))
    ).properties(
        width=700,
        height=400
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

def create_control_card(title, component_id, component):
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, className="card-title", style={"font-size": "18px"}),
            component
        ]),
        className="mb-2",
        style={"width": "80%", "height": "38rem", "padding": "0.5rem"}
    )

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Label("Select Province/Territory"),
            province_dropdown
        ], width=3)
    ], className="mb-1 justify-content-center"),

    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H4("Maple Eagle Trade Tracker", className="text-center")
                ]), style={"width": "80%", "height": "6.8rem", "margin-top": "0rem"}  
            ),
            html.Br(),
            create_control_card("Select Trade Sector", "sector-dropdown", sector_checklist)
        ], width=2, style={"padding": "0.2rem", "margin-right": "-3rem"}), 

        dbc.Col([
            dbc.Row([
                dbc.Col(dbc.Card(id="import_card", style={"width": "18rem", "padding": "0.2rem"}), width=3, style={"margin-left": "5.5rem"}), 
                dbc.Col(dbc.Card(id="export_card", style={"width": "18rem", "padding": "0.2rem"}), width=3, style={"margin-left": "5.5rem"}),
                dbc.Col(create_chart_card_trend_line("Trade Balance Over Time", "trade_balance_chart"), width=4, style={"margin-left": "1.4rem"})  
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
                dbc.Col(create_chart_card("Imports from the US in 2024 by Sector", "bar2", height="13rem"), width=6, style={"width": "43rem"}),
                dbc.Col(create_chart_card("Exports to the US in 2024 by Sector", "bar1", height="13rem"), width=6, style={"width": "43rem"})
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



@app.callback(
    [Output("import_card", "children"),
     Output("export_card", "children")],
    [Input("province-dropdown", "value"),
     Input("sector-dropdown", "value")]
)
def update_total_trade_card(selected_provinces, selected_sectors):
    filtered_df = df.copy()

    if "All" not in selected_provinces:
        filtered_df = filtered_df[filtered_df["PROVINCE"].isin(selected_provinces)]
    if "All" not in selected_sectors:
        filtered_df = filtered_df[filtered_df["SECTOR"].isin(selected_sectors)]

    import_card_body = create_total_trade_card(filtered_df, "import").children  
    export_card_body = create_total_trade_card(filtered_df, "export").children  

    return import_card_body, export_card_body

@app.callback(
    Output("trade_balance_chart", "spec"),
    [Input("province-dropdown", "value"),
     Input("sector-dropdown", "value")]
)
def update_net_trade_lineplot(selected_provinces, selected_sectors):
    filtered_df = df.copy()

    if "All" not in selected_provinces:
        filtered_df = filtered_df[filtered_df["PROVINCE"].isin(selected_provinces)]
    if "All" not in selected_sectors:
        filtered_df = filtered_df[filtered_df["SECTOR"].isin(selected_sectors)]

    net_trade_lineplot = create_net_trade_lineplot(filtered_df)
    return net_trade_lineplot

@app.callback(
    Output('bar1', 'spec'),
    Input('province-dropdown', 'value')
)
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

@app.callback(
    Output('bar2', 'spec'),
    Input('province-dropdown', 'value')
)
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

@app.callback(
    Output("trade_geographical_map", "spec"),
    [Input("province-dropdown", "value"),
     Input("sector-dropdown", "value")]
)
def update_map_chart(selected_province, selected_sector):
    """Updates the trade map based on user selections"""
    
    filtered_df = processed_df.copy()

    if selected_sector and (isinstance(selected_sector, list) and selected_sector != ['All']):
        filtered_df = filtered_df[filtered_df["SECTOR"].isin(selected_sector)]

    updated_chart = get_map_chart(filtered_df, selected_province)

    return updated_chart.to_dict(format="vega")

@app.callback(
    [Output("historical_import_chart", "spec"),
     Output("historical_export_chart", "spec")],
    [Input("province-dropdown", "value"),
     Input("sector-dropdown", "value")]
)
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

if __name__ == '__main__':
    app.run_server(debug=False)
