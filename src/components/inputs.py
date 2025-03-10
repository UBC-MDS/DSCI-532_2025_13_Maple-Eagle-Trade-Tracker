from dash import dcc
import pandas as pd
from data import clean_data

df = clean_data()

province_options = [
    {'label': province, 'value': province} for province in sorted(df['PROVINCE'].dropna().unique())
]

province_checklist = dcc.Checklist(
    id='province-dropdown',
    options=province_options,
    value=[province_options[0]["value"]],  
    inputStyle={"margin-right": "5px", "margin-left": "10px"},  
    labelStyle={
        "display": "block", 
        "margin-left": "20px", 
        "text-indent": "-29px",
        "font-size": "12px"  
    },
    style={"max-width": "180px", "word-wrap": "break-word"}
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