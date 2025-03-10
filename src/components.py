from dash import dcc
import pandas as pd

df = pd.read_csv('data/clean/clean_data.csv')

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