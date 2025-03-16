import geopandas as gpd
import logging
from utils import save_dataframe

def load_canadian_provinces(
        url: str = 'https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip',
        save_to: str = "./data/processed/canadian_provinces.parquet"
) -> None:
    """
    Load Canadian provinces geometries from a specified URL and save them to a CSV file.
    
    Parameters
    ----------
    url (str): The URL to download the Canadian provinces geometries. Defaults to the Natural Earth dataset URL.
    save_to (str): The file path to save the processed Canadian provinces data as a CSV file. Defaults to "../data/processed/canadian_provinces.csv".
    
    Returns
    ----------
    None
    
    Raises
    ------
    Exception: 
        If there is an error writing the data to the specified file path.
    """
    
    provinces = gpd.read_file(url).query("iso_a2 == 'CA'")[['name', 'geometry']]
    provinces['name'] = provinces['name'].astype('category')
    provinces.columns = [col.upper() for col in provinces.columns]
    provinces = gpd.GeoDataFrame(provinces, geometry='GEOMETRY')

    try:
        if save_to.endswith('.csv'):
            save_dataframe(provinces, save_to, format="csv")
        else:
            save_dataframe(provinces, save_to, format="parquet")
    except Exception as e:
        logging.error(f"Error writing to {save_to}: {e}")


if __name__ == "__main__":
    load_canadian_provinces()