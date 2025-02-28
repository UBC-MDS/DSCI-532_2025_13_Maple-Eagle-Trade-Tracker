from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import pandas as pd


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
    clearable=False,
)

sector_dropdown = dcc.Dropdown(
    id='sector-dropdown',
    options=sector_options,
    value='All',
    clearable=False,
)

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

    dcc.Graph(id="trade_balance_chart"),

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
        dcc.Graph(id="historical_import_chart", style={'width': '30%', 'display': 'inline-block'}),
        dcc.Graph(id="historical_export_chart", style={'width': '30%', 'display': 'inline-block'})
    ])
])

if __name__ == '__main__':
    app.run_server(debug=False)
