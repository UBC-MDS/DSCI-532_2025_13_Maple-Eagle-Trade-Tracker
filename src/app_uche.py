import altair as alt
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_vega_components as dvc
import geopandas as gpd
import pandas as pd
import plotly.express as px

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

df = pd.read_csv('data/clean/clean_data.csv')

province_options = [{'label': 'All', 'value': 'All'}] + [
    {'label': province, 'value': province} for province in sorted(df['PROVINCE'].dropna().unique())
]

sector_options = [{'label': 'All', 'value': 'All'}] + [
    {'label': sector, 'value': sector} for sector in sorted(df['SECTOR'].dropna().unique())
]

province_dropdown = dcc.Dropdown(
    id='province-dropdown',
    options=province_options,
    value='All',
    multi = True,
    clearable=False,
)

sector_dropdown = dcc.Dropdown(
    id='sector-dropdown',
    options=sector_options,
    value='All',
    multi = True,
    clearable=False,
)

def create_historical_chart(filtered_df, trade_flow, title):
    grouped_df = filtered_df.groupby("YEAR", as_index=False).agg({"VALUE": "sum"})
    fig = px.bar(
        grouped_df,
        x="YEAR",
        y="VALUE",
        title=title,
        labels={"VALUE": title, "YEAR": "Year"},
    )
    return fig

def get_agg_geom_data(df):
    """Aggregate the geometric data"""
    
    url = 'https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip'
    canadian_provinces = gpd.read_file(url).query("iso_a2 == 'CA'")[
        ['name', 'geometry']
    ]
    canadian_provinces.columns = [col.upper() for col in canadian_provinces.columns]
    
    aggr_data = df.groupby('PROVINCE')[['NET_TRADE']].sum().reset_index()
    geo_data = aggr_data.merge(canadian_provinces, how='inner', 
                               left_on='PROVINCE', right_on='NAME')
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
    # Full color scale for net trade across all provinces
    # Conditional coloring: selected provinces use the net trade scale, others are light gray
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

processed_df = pd.read_csv('data/clean/processed_data.csv') 
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H4("Total Imports (CAD)"),
            html.H2("$XX Billion", id="kpi_imports")
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'display': 'inline-block'}),

        html.Div([
            html.H4("Total Exports (CAD)"),
            html.H2("$XX Billion", id="kpi_exports")
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justify-content': 'space-around'}),

    html.Div(
        [dvc.Vega(id="trade_geographical_map", spec=get_map_chart(processed_df, ['All']).to_dict(format="vega"))],
        style={
        'display': 'flex', 
        'justifyContent': 'center', 
        'alignItems': 'center', 
        'height': '80vh'  # Ensures vertical centering within viewport
        }
    ), 

    html.Div([
        dcc.Graph(id="import_bar_chart", style={'width': '30%', 'display': 'inline-block'}),
        dcc.Graph(id="export_bar_chart", style={'width': '30%', 'display': 'inline-block'}),
        dcc.Graph(id="trade_balance_map", style={'width': '40%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justify-content': 'space-around'}),

    html.Div([
        html.Div([
            html.Label("Select Trade Sector"),
            sector_dropdown,
        ], style={'width': '20%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Select Province/Territory"),
            province_dropdown,
        ], style={'width': '20%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justify-content': 'space-around'}),

    html.Div([
        dcc.Graph(
            id="historical_import_chart",
            figure=create_historical_chart(df[df["TRADE_FLOW"] == "Import"], "Import", "Annual Import"),  
            style={'width': '45%', 'display': 'inline-block'}
        ),
        dcc.Graph(
            id="historical_export_chart",
            figure=create_historical_chart(df[df["TRADE_FLOW"] == "Domestic export"], "Domestic export", "Annual Export"),  
            style={'width': '45%', 'display': 'inline-block'}
        )
    ])
])

# @app.callback(
#     [Output("historical_import_chart", "figure"),
#      Output("historical_export_chart", "figure")],
#     [Input("province-dropdown", "value"),
#      Input("sector-dropdown", "value")]
# )

# def update_historical_charts(selected_province, selected_sector):
#     filtered_df = df.copy()
#     if selected_province != "All":
#         filtered_df = filtered_df[filtered_df["PROVINCE"] == selected_province]
#     if selected_sector != "All":
#         filtered_df = filtered_df[filtered_df["SECTOR"] == selected_sector]
    
#     import_df = filtered_df[filtered_df["TRADE_FLOW"] == "Import"]
#     export_df = filtered_df[filtered_df["TRADE_FLOW"] == "Domestic export"]
    
#     import_chart = create_historical_chart(import_df, "Import", "Annual Import")
#     export_chart = create_historical_chart(export_df, "Domestic export", "Annual Export")
    
#     return import_chart, export_chart


@app.callback(
    Output("trade_geographical_map", "spec"),
    [Input("province-dropdown", "value"),
     Input("sector-dropdown", "value")]
)
def update_map_chart(selected_province, selected_sector):
    """Updates the trade map based on user selections"""
    
    data_path = "data/clean/processed_data.csv"
    processed_data = pd.read_csv(data_path)
    
    filtered_df = processed_data.copy()

    if selected_sector and (isinstance(selected_sector, list) and selected_sector != ['All']):
        filtered_df = filtered_df[filtered_df["SECTOR"].isin(selected_sector)]


    # Generate updated chart with filtered data
    updated_chart = get_map_chart(filtered_df, selected_province)

    return updated_chart.to_dict(format="vega")


if __name__ == '__main__':
    app.run_server(debug=False)
