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

province_dropdown = dcc.Dropdown(
    id='province-dropdown',
    options=province_options,
    value=['All'],
    clearable=False,
    multi=True
)

sector_dropdown = dcc.Dropdown(
    id='sector-dropdown',
    options=sector_options,
    value=['All'],
    clearable=False,
    multi=True
)

def create_net_trade_lineplot(df):
    reshaped_df = df.pivot(index=['YEAR_MONTH', 'YEAR', 'PROVINCE', 'SECTOR'],
                           columns='TRADE_FLOW', 
                           values='FULL_VALUE').reset_index()

    reshaped_df['NET'] = reshaped_df['Domestic export'] - reshaped_df['Import']
    df_annual = reshaped_df.groupby(['YEAR', 'PROVINCE', 'SECTOR']).agg({'NET': 'sum'}).reset_index()
    df_annual = df_annual.groupby('YEAR').agg({'NET': 'sum'}).reset_index()

    chart = (
        alt.Chart(df_annual)
        .mark_line(point=True)
        .encode(
            x=alt.X("YEAR:O", title="Year"),
            y=alt.Y("NET:Q", title="Net Trade"),
            tooltip=["YEAR", "NET"]
        )
        .properties(
            title="Aggregate Net Trade by Year",
            width=600,
            height=400
        )
        .configure_axis(grid=True)
        .interactive()
    )

    return chart.to_dict()

def create_total_trade_card(df, trade_flow):
    max_year = max(df['YEAR'])

    sum_by_trade_df = df[df['YEAR'] == max_year].groupby('TRADE_FLOW')['VALUE'].sum()

    if trade_flow.lower() == 'import':
        total_trade_value = sum_by_trade_df.get("Import", 0)
        title = "Total Import Value in CAD ($)"
        text_color = 'red'
    else:
        total_trade_value = sum_by_trade_df.get("Domestic export", 0)
        title = "Total Export Value in CAD ($)"
        text_color = 'green'

    card = dbc.Card(
        dbc.CardBody([
            html.H4(title, className="card-title"),
            html.P(f"${total_trade_value:,.2f}",
                   className="card-text",
                   style={"color": text_color})
        ]),
        style={"width": "18rem"},
    )

    return card

def create_historical_chart(filtered_df, title):
    grouped_df = filtered_df.groupby("YEAR", as_index=False).agg({"VALUE": "sum"})
    
    chart = (
        alt.Chart(grouped_df)
        .mark_bar()
        .encode(
            x=alt.X("YEAR:O", title="Year"),
            y=alt.Y("VALUE:Q", title=title),
            tooltip=["YEAR", "VALUE"]
        )
        .properties(title=title, width=400, height=300)
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

    map_chart = alt.Chart(aggr_data, width=600, height=500).mark_geoshape(
        strokeWidth=2
    ).encode(
        tooltip=['PROVINCE:N', alt.Tooltip('NET_TRADE:Q', format=',')],
        color=color_encoding, 
        stroke=alt.condition(hover, alt.value('white'), alt.value('#222222')),
        order=alt.condition(hover, alt.value(1), alt.value(0))
    ).properties(
        width=600,
        height=500
    ).configure(
        background='transparent'
    ).project(
        'transverseMercator',
        rotate=[90, 0, 0]
    ).add_params(
        hover
    )

    return map_chart


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('Maple-Eagle-Trade-Tracker'),
            html.Br(),
        ]),
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Label("Select Trade Sector"),
            sector_dropdown,
        ], width=6),
        
        dbc.Col([
            html.Label("Select Province/Territory"),
            province_dropdown,
        ], width=6)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([html.H1('Maple-Eagle-Trade-Tracker'), html.Br()])
    ]),


    dbc.Row([
        dbc.Col([dbc.Card(id="import_card")], width=6),
        dbc.Col([dbc.Card(id="export_card")], width=6)
    ]),

    dbc.Row([
        dbc.Col([dvc.Vega(id="trade_balance_chart")], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dvc.Vega(id='bar1', spec={})
        ], md=6),
        dbc.Col([
            dvc.Vega(id='bar2', spec={})
        ], md=6)
    ]),
    
    dbc.Row([
        dbc.Col([
            dvc.Vega(
                id="historical_import_chart",
                spec=create_historical_chart(df[df["TRADE_FLOW"] == "Import"], "Annual Import"),  
                style={'width': '100%'}
            )
        ], width=6),
        
        dbc.Col([
            dvc.Vega(
                id="historical_export_chart",
                spec=create_historical_chart(df[df["TRADE_FLOW"] == "Domestic export"], "Annual Export"),  
                style={'width': '100%'}
            )
        ], width=6)
    ]),

    dbc.Row([
        dbc.Col([
            dvc.Vega(
                id="trade_geographical_map",
                spec=get_map_chart(processed_df, ['All']).to_dict(format="vega"),  
                style={'width': '100%'}
            )
        ], width=12)
    ])
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

    import_card = create_total_trade_card(filtered_df, "import")
    export_card = create_total_trade_card(filtered_df, "export")

    return import_card, export_card

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
            width=500,
            height=400,
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
                alt.Tooltip('sum(FULL_VALUE)', title='Total import value:', format=',')  # Format for readability
            ]
        ).properties(
            width=500,
            height=400,
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
