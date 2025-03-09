import pandas as pd
import logging
from typing import Optional

logging.basicConfig(level=logging.WARNING)

def preprocess_data_and_calculate_net_trade(input_path: str = "../data/clean/clean_data.csv", 
                                            save_to: str = "../data/clean/processed_data.csv") -> None:
    """
    Calculate net trade and preprocess data from a CSV file.
    This function reads trade data from a CSV file, preprocesses it by pivoting the data,
    calculates the net trade (EXPORT - IMPORT), and saves the processed data to a new CSV file.
    
    Parameters
    ----------
    input_path : str
        The file path to the input CSV file containing the trade data. Default is "../data/clean/clean_data.csv".
    save_to : str
        The file path to save the processed data CSV file. Default is "../data/clean/processed_data.csv".
    
    Returns
    ----------
    None
    
    Raises
    ------
    FileNotFoundError
        Logs errors if the input file is not found, is empty, or cannot be read.
    Logs warnings if the 'EXPORT' or 'IMPORT' columns are missing, skipping net trade calculation.
    Logs errors if there is an issue writing the processed data to the output file.
    """
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        logging.error(f"File not found: {input_path}")
        return
    except pd.errors.EmptyDataError:
        logging.error(f"No data: {input_path}")
        return
    except Exception as e:
        logging.error(f"Error reading {input_path}: {e}")
        return

    df = df.drop(columns=['VALUE'], errors='ignore')

    index_columns = list(set(df.columns) - set(['TRADE_FLOW', 'FULL_VALUE']))

    preprocessed_data = df.pivot_table(values='FULL_VALUE', index=index_columns, 
                                       columns='TRADE_FLOW').reset_index()
    preprocessed_data.columns = [col.upper() for col in preprocessed_data.columns]
    preprocessed_data['PROVINCE'] = preprocessed_data['PROVINCE'].replace({'Quebec': 'Québec'})
    preprocessed_data['PROVINCE'] = preprocessed_data['PROVINCE'].str.strip().astype('category')
    
    if 'DOMESTIC EXPORT' in preprocessed_data.columns:
        preprocessed_data.rename(columns={'DOMESTIC EXPORT': 'EXPORT'}, inplace=True)

    if {'EXPORT', 'IMPORT'}.issubset(preprocessed_data.columns):
        preprocessed_data['NET_TRADE'] = preprocessed_data['EXPORT'] - preprocessed_data['IMPORT']
    else:
        logging.warning("Warning: 'EXPORT' or 'IMPORT' column is missing, skipping NET TRADE calculation.")

    try:
        preprocessed_data.to_csv(save_to, index=False)
    except Exception as e:
        logging.error(f"Error writing to {save_to}: {e}")

if __name__ == "__main__":
    preprocess_data_and_calculate_net_trade()