import geopandas as gpd
import pandas as pd
import shapely.wkt
import os
from functools import cache
import sys

# Get the absolute path of the root project directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# Add 'scripts/' to sys.path
scripts_path = os.path.join(project_root, "scripts")
sys.path.append(scripts_path)
from save_province_data import load_canadian_provinces

DATA_PATH = "src/data/processed/canadian_provinces.parquet"

@cache
def get_provinces_data():
    """Load Canadian provinces geometries from a local file, or download if not found."""
    
    if not os.path.exists(DATA_PATH):
        print("🔄 Local file not found. Downloading provinces data...")
        url = "https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip"
        provinces = load_canadian_provinces(url, DATA_PATH)
        
        # provinces.to_parquet(DATA_PATH)
        print(f"📁 Data saved to {DATA_PATH}")

    print("✅ Loading provinces data from local file...")
    provinces = gpd.read_parquet(DATA_PATH)

    if provinces["geometry"].dtype == "object":  # If stored as WKT, convert back
        provinces["geometry"] = provinces["geometry"].apply(shapely.wkt.loads)

    provinces = gpd.GeoDataFrame(provinces, geometry="geometry")

    return provinces


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
    """Aggregate the geometric data using local processed province data."""

    canadian_provinces = get_provinces_data()

    if 'NET_TRADE' not in df.columns:
        raise KeyError("NET_TRADE column is missing from the processed dataset.")
    aggr_data = df.groupby('PROVINCE')[['NET_TRADE']].sum().reset_index()

    # Merge with province geometry
    geo_data = aggr_data.merge(canadian_provinces, how='inner', left_on='PROVINCE', right_on='name')
    geo_data = geo_data.drop(columns=['name'])
    geo_data = gpd.GeoDataFrame(geo_data, geometry="geometry")
    
    return geo_data


def get_processed_data_abb(
    data_path = '../data/processed/processed_data_abb.csv'
):
    """Returns the processed data with abbreviated sector names"""
    processed_df = pd.read_csv(data_path)
    
    return processed_df
