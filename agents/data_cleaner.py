import pandas as pd

DEFAULT_NUMERIC_VALUE = 0.0
DEFAULT_TEXT_VALUE = "Unknown"

def _compute_fill_value(series: pd.Series, method: str):
    if method =="mean":
        return series.mean(skipna=True) if pd.api.types.is_numeric_dtype(series) else series.mode().iloc[0] if not series.mode().empty else DEFAULT_TEXT_VALUE
    elif method == "median":
        return series.median(skipna=True) if pd.api.types.is_numeric_dtype(series) else series.mode().iloc[0] if not series.mode().empty else DEFAULT_TEXT_VALUE
    elif method == "mode":
        return series.mode().iloc[0] if not series.mode().empty else DEFAULT_TEXT_VALUE
    else:
        return DEFAULT_NUMERIC_VALUE if pd.api.types.is_numeric_dtype(series) else DEFAULT_TEXT_VALUE
    

def clean_data(df: pd.DataFrame, cleaning_plan: dict): 
    df_cleaned = df.copy()
    audit_log = []
    
    cleaning_plan = {col: (method or "").strip().lower() for col, method in cleaning_plan.items()}

    #removing rows more than 1 missing values
    rows_before = len(df_cleaned)
    multi_missing_mask = df_cleaned.isna().sum(axis=1) > 1
    rows_to_drop = df_cleaned[multi_missing_mask]
    if not rows_to_drop.empty:
        df_cleaned = df_cleaned.loc[~multi_missing_mask]
        audit_log.append(f'Dropped {len(rows_to_drop)} rows with more than 1 missing value')
    

    #Filling values as requested
    for idx,row in df_cleaned.iterrows():
        missing_cols = row[row.isna()].index.to_list()
        if len(missing_cols) ==1:
            col = missing_cols[0]
            if col in cleaning_plan:
                method = cleaning_plan[col]
                fill_val = _compute_fill_value(df_cleaned[col],method)
                df_cleaned.at[idx,col] =fill_val
                audit_log.append(f"Row {idx}: Filled '{col}' with '{fill_val}' using {method}")
            else:
                audit_log.append(f"Row {idx}: Missing value in '{col}' but no plan provided")
    
    #Ensure JSON-safe values when returning through API (NaN -> None)
    df_cleaned = df_cleaned.fillna({col: DEFAULT_NUMERIC_VALUE if pd.api.types.is_numeric_dtype(df_cleaned[col]) else DEFAULT_TEXT_VALUE for col in df_cleaned.columns})
    return df_cleaned.reset_index(drop=True), audit_log

def check_for_date(df):
    data = df.copy()
    for col in data.columns:
        if 'date' in col.lower():
            try:
                data[col] = pd.to_datetime(data[col], errors='coerce')
            except Exception as e:
                print(f"Could not convert column '{col}' to datetime: {e}")
    return data
    
