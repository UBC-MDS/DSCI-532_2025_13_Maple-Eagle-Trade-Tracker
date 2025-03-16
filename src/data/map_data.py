import geopandas as gpd
import pandas as pd

from functools import cache

# @cache
def get_provinces_data(
    data_path = '../data/processed/canadian_provinces.parquet'
):
    """Load Canadian provinces geometries"""
    if data_path.endswith('.parquet'):
        provinces = gpd.read_parquet(data_path)
        provinces['GEOMETRY'] = provinces['GEOMETRY'].apply(lambda geom: geom.__geo_interface__)
    else:
        provinces = pd.read_csv(data_path)
    # provinces = gpd.GeoDataFrame(provinces, geometry='GEOMETRY')

    return provinces

# @cache
def get_processed_data(
    data_path = '../data/processed/processed_data.parquet'
):
    """Returns the processed data"""
    if data_path.endswith('.parquet'):
        processed_df = pd.read_parquet(data_path)
    else:
        processed_df = pd.read_csv(data_path) 
    
    return processed_df


def get_agg_geom_data(df):
    """Aggregate the geometric data using processed_df"""
    
    url = 'https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip'
    canadian_provinces = gpd.read_file(url).query("iso_a2 == 'CA'")[
        ['name', 'geometry']
    ]
    canadian_provinces.columns = [col.upper() for col in canadian_provinces.columns]

    if 'NET_TRADE' not in df.columns:
        raise KeyError("NET_TRADE column is missing from the processed dataset.")

    aggr_data = df.groupby('PROVINCE')[['NET_TRADE']].sum().reset_index()
    geo_data = aggr_data.merge(canadian_provinces, how='inner', left_on='PROVINCE', right_on='NAME')
    geo_data = geo_data.drop(columns=['NAME'])
    geo_data = gpd.GeoDataFrame(geo_data, geometry='GEOMETRY')

    return geo_data

# def get_agg_geom_data(df):
#     """Aggregate the geometric data using processed_df"""

#     canadian_provinces = get_provinces_data()

#     if 'NET_TRADE' not in df.columns:
#         raise KeyError("NET_TRADE column is missing from the processed dataset.")

#     aggr_data = df.groupby('PROVINCE')[['NET_TRADE']].sum().reset_index()
#     geo_data = aggr_data.merge(canadian_provinces, how='inner', left_on='PROVINCE', right_on='NAME')
#     geo_data = geo_data.drop(columns=['NAME'])

#     return geo_data