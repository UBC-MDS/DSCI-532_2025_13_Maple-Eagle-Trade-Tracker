import pandas as pd

def clean_data():
    df = pd.read_csv('../data/raw/StatsCan_RawData.csv')

    ## select relevant columns 
    df = df[['REF_DATE', 'YEAR', 'GEO', 'Trade', 'North American Product Classification System (NAPCS)', 'Principal trading partners', 'VALUE', 'FULL_VALUE']]

    ## rename columns 
    df.columns = ['YEAR_MONTH', 'YEAR', 'PROVINCE', 'TRADE_FLOW', 'SECTOR', 'TRADE_PARTNER', 'VALUE', 'FULL_VALUE']

    df['YEAR'] = df['YEAR'].apply(lambda x: pd.to_datetime(x, format='%Y').year)
    df['YEAR_MONTH'] = df['YEAR_MONTH'].apply(lambda x: pd.to_datetime(x, format='%Y-%m'))
    df['SECTOR'] = df['SECTOR'].str.replace('\s*\[.*?\]', '', regex=True)

    return df

   
df = clean_data