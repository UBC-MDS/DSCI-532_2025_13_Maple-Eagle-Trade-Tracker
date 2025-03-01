import altair as alt
import pandas as pd
import dash_bootstrap_components as dbc
import dash_vega_components as dvc
from dash import Dash, dcc, callback, Output, Input, html
from vega_datasets import data


# Initiatlize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df = pd.read_csv('../data/clean/clean_data.csv')

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('Maple-Eagle-Trade-Tracker'),
            html.Br(),
        ]),
    ]),
    dbc.Row([
        dbc.Col(
            [
                dbc.Label('Select province'),
                dcc.Checklist(id='province', 
                 options=df['PROVINCE'].value_counts().index, 
                 value=['Newfoundland and Labrador', 'Prince Edward Island', 'Nova Scotia',
                        'New Brunswick', 'Quebec', 'Ontario', 'Manitoba', 'Saskatchewan',
                        'Alberta', 'British Columbia', 'Yukon', 'Northwest Territories',
                        'Nunavut']),
                html.Br(),
            ],
            md=3
        ),
        dbc.Col(
            [
                dbc.Row(
                    dbc.Col(
                        dvc.Vega(id='bar1', spec={})     
                    )
                ),
                dbc.Row(
                    dbc.Col(
                        dvc.Vega(id='bar2', spec={})     
                    )
                )
            ],
            md=4
        )
    ]),
])

# Server side callbacks/reactivity
@callback(
    Output('bar1', 'spec'),
    Input('province', 'value')
)
def create_chart(province):
    return(
        alt.Chart(df[(df['YEAR'] == 2024) & (df['TRADE_FLOW'] == 'Domestic export') & df['PROVINCE'].isin(province)]).mark_bar().encode(
        x=alt.X('FULL_VALUE', title='Value'),
        y=alt.Y('SECTOR', title='Sector', axis=alt.Axis(labelLimit=400, titlePadding=80)).sort('-x'),
        ).properties(
            width=500,
            height=400,
            title='Exports to the US in 2024 by sector'
        ).to_dict()
        )

@callback(
    Output('bar2', 'spec'),
    Input('province', 'value')
)
def create_chart(province):
    return(
        alt.Chart(df[(df['YEAR'] == 2024) & (df['TRADE_FLOW'] == 'Import') & df['PROVINCE'].isin(province)]).mark_bar().encode(
        x=alt.X('FULL_VALUE', title='Value'),
        y=alt.Y('SECTOR', title='Sector', axis=alt.Axis(labelLimit=400, titlePadding=80)).sort('-x'),
        ).properties(
            width=500,
            height=400,
            title='Imports from the US in 2024 by sector'
        ).to_dict()
        )

# Run the app/dashboard
if __name__ == '__main__':
    app.server.run(port=8000, host='127.0.0.1')