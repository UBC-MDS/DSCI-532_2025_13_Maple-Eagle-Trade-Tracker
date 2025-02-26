from dash import Dash, html, dcc

app = Dash(__name__)

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
            dcc.Dropdown(id="sector_filter", options=[], multi=True),
        ], style={'width': '20%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Select Province/Territory"),
            dcc.Dropdown(id="province_filter", options=[], multi=True),
        ], style={'width': '20%', 'display': 'inline-block'}),

        dcc.Graph(id="historical_import_chart", style={'width': '30%', 'display': 'inline-block'}),
        dcc.Graph(id="historical_export_chart", style={'width': '30%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justify-content': 'space-around'})
])

if __name__ == '__main__':
    app.run(debug=True)