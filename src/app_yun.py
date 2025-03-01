from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import altair as alt
import dash_vega_components as dvc

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

app.layout = html.Div([
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
        dvc.Vega(
            id="historical_import_chart",
            spec=create_historical_chart(df[df["TRADE_FLOW"] == "Import"], "Annual Import"),  
            style={'width': '45%', 'display': 'inline-block'}
        ),
        dvc.Vega(
            id="historical_export_chart",
            spec=create_historical_chart(df[df["TRADE_FLOW"] == "Domestic export"], "Annual Export"),  
            style={'width': '45%', 'display': 'inline-block'}
        )
    ])
])

@app.callback(
    [Output("historical_import_chart", "spec"),
     Output("historical_export_chart", "spec")],
    [Input("province-dropdown", "value"),
     Input("sector-dropdown", "value")]
)
def update_historical_charts(selected_provinces, selected_sectors):
    if not selected_provinces:
        selected_provinces = [province_options[1]['value']]  
    if not selected_sectors:
        selected_sectors = [sector_options[1]['value']]  
    
    filtered_df = df.copy()
    
    if "All" not in selected_provinces:
        filtered_df = filtered_df[filtered_df["PROVINCE"].isin(selected_provinces)]
    if "All" not in selected_sectors:
        filtered_df = filtered_df[filtered_df["SECTOR"].isin(selected_sectors)]
    
    import_df = filtered_df[filtered_df["TRADE_FLOW"] == "Import"]
    export_df = filtered_df[filtered_df["TRADE_FLOW"] == "Domestic export"]
    
    import_chart = create_historical_chart(import_df, "Annual Import")
    export_chart = create_historical_chart(export_df, "Annual Export")
    
    return import_chart, export_chart

if __name__ == '__main__':
    app.run_server(debug=False)
