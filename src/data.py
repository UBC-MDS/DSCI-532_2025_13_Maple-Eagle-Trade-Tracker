import geopandas as gpd
import pandas as pd

from functools import cache

@cache
def load_canadian_provinces():
    """Load Canadian provinces geometries"""
    
    url = 'https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip'
    provinces = gpd.read_file(url).query("iso_a2 == 'CA'")[['name', 'geometry']]
    provinces['name'] = provinces['name'].astype('category')
    provinces.columns = [col.upper() for col in provinces.columns]

    return provinces

@cache
def get_processed_data():
    """Returns the processed data"""

    processed_df = pd.read_csv('data/clean/processed_data.csv') 
    return processed_df


def get_agg_geom_data(df):
    """Aggregate the geometric data using processed_df"""

    canadian_provinces = load_canadian_provinces()

    if 'NET_TRADE' not in df.columns:
        raise KeyError("NET_TRADE column is missing from the processed dataset.")

    aggr_data = df.groupby('PROVINCE')[['NET_TRADE']].sum().reset_index()
    geo_data = aggr_data.merge(canadian_provinces, how='inner', left_on='PROVINCE', right_on='NAME')
    geo_data = geo_data.drop(columns=['NAME'])
    geo_data = gpd.GeoDataFrame(geo_data, geometry='GEOMETRY')

    return geo_data
