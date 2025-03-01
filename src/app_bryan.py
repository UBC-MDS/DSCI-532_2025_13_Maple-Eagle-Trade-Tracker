from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import altair as alt
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
    clearable=False,
)
sector_dropdown = dcc.Dropdown(
    id='sector-dropdown',
    options=sector_options,
    value='All',
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

def create_net_trade_lineplot(df):

    reshaped_df = df.pivot(index= ['YEAR_MONTH', 'YEAR', 'PROVINCE', 'SECTOR'],
                           columns='TRADE_FLOW', 
                           values='FULL_VALUE').reset_index()
    
    reshaped_df['NET'] = reshaped_df['Domestic export'] - reshaped_df['Import']
    df_annual = reshaped_df.groupby(['YEAR','PROVINCE','SECTOR']).agg({'NET': 'sum'}).reset_index()
    df_annual = df_annual.groupby('YEAR').agg({
        'NET': 'sum',
        }).reset_index()
    
    fig = px.line(df_annual,
                  x="YEAR",
                  y="NET",
                  title='Aggregate Net Trade by Year',
                  subtitle='Net Trade is defined as total exports subtracted by total imports to represent our trade surplus',
                  labels={"VALUE": 'NET TRADE', "YEAR": "Year"},
                  )
    return fig

def create_total_trade_card(df, trade_flow):
    max_year = max(df['YEAR'])

    try:
        if trade_flow.lower() not in ['import','export']:
            raise ValueError("trade_flow is not import or export")
    except ValueError as e:
        print(e)

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
        dbc.CardBody(
            [
                html.H4(title, className="card-title"),
                html.P(
                    f"${total_trade_value:,.2f}",
                    className="card-text",
                    style={"color": text_color}
                )
            ]
        ),
        style={"width": "18rem"},
    )

    return card

app.layout = html.Div([
    html.Div([
        html.Div([
            dbc.Card(
                id="import_card",
                children=create_total_trade_card(df, "import"),
                style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'display': 'inline-block'}
            ),
        ],
        id="import_card_div",
        style={'display': 'inline-block', 'width': '45%'}),

        html.Div([
            dbc.Card(
                id="export_card",
                children=create_total_trade_card(df, "export"),
                style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'display': 'inline-block'}
            ),
        ],
        id="export_card_div",
        style={'display': 'inline-block', 'width': '45%'})
        ], style={'display': 'flex', 'justify-content': 'space-around'}),

    dcc.Graph(id="trade_balance_chart",
              figure=create_net_trade_lineplot(df),
              style={'width': '85%', 'display': 'inline-block'}),

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

@app.callback(
    [Output("historical_import_chart", "figure"),
     Output("historical_export_chart", "figure")],
    [Input("province-dropdown", "value"),
     Input("sector-dropdown", "value")]
)

def update_historical_charts(selected_province, selected_sector):
    filtered_df = df.copy()
    if selected_province != "All":
        filtered_df = filtered_df[filtered_df["PROVINCE"] == selected_province]
    if selected_sector != "All":
        filtered_df = filtered_df[filtered_df["SECTOR"] == selected_sector]
    
    import_df = filtered_df[filtered_df["TRADE_FLOW"] == "Import"]
    export_df = filtered_df[filtered_df["TRADE_FLOW"] == "Domestic export"]
    
    import_chart = create_historical_chart(import_df, "Import", "Annual Import")
    export_chart = create_historical_chart(export_df, "Domestic export", "Annual Export")
    
    return import_chart, export_chart

@app.callback(
    [Output("import_card", "children"),
     Output("export_card", "children")],
    [Input("province-dropdown", "value"),
     Input("sector-dropdown", "value")]
)
def update_total_trade_card(selected_province, selected_sector):
    filtered_df = df.copy()

    if selected_province != "All":
        filtered_df = filtered_df[filtered_df["PROVINCE"] == selected_province]
    if selected_sector != "All":
        filtered_df = filtered_df[filtered_df["SECTOR"] == selected_sector]

    import_card = create_total_trade_card(filtered_df, "import")
    export_card = create_total_trade_card(filtered_df, "export")

    return import_card, export_card

@app.callback(
    Output("trade_balance_chart", "figure"),
    [Input("province-dropdown", "value"),
     Input("sector-dropdown", "value")]
)

def update_net_trade_lineplot(selected_province, selected_sector):
    filtered_df = df.copy()

    if selected_province != "All":
        filtered_df = filtered_df[filtered_df["PROVINCE"] == selected_province]
    if selected_sector != "All":
        filtered_df = filtered_df[filtered_df["SECTOR"] == selected_sector]

    net_trade_lineplot = create_net_trade_lineplot(filtered_df)

    return net_trade_lineplot

if __name__ == '__main__':
    app.run_server(debug=False)
    
