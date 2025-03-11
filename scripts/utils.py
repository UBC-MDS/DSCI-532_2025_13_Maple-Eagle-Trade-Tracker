import os

def save_dataframe(df, file_path, format="csv"):
    """
    Save a DataFrame to a CSV or Parquet file.
    
    Parameters
    ----------
    df : pd.DataFrame 
        The DataFrame to save.
    file_path : str
        The path to save the file.
    format : str
        The format to save as ("csv" or "parquet").
    
    Returns
    ----------
    None
    """
    
    accepted_formats = ["csv", "parquet"]
    if format not in accepted_formats:
        raise ValueError(f"Unsupported file format. Use one of the following: {accepted_formats}.")
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  
    
    if format == "csv":
        df.to_csv(file_path, index=False)
    else:
        df.to_parquet(file_path, index=False)

    return


