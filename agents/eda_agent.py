import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import os, math
from scipy.stats import entropy

matplotlib.use("Agg")

def needs_eda(df):
    if df.isnull().sum().sum() > 0:
        return True, "Dataset has missing Values."
    if df.shape[1]> 20:
        return True, f"Dataset has {df.shape[1]} columns. EDA recommended"
    if df.select_dtypes(include=['object']).shape[1]>0:
        return True,"Dataset has categorical or textual data"
    if df.duplicated().sum()>100:
        return True, "Dataset has a large number of duplicates"
    return True, "Datasets apperas clean. EDA optional"

def get_missing_columns(df: pd.DataFrame) ->dict:
    missing_info = df.isnull().sum()
    return missing_info[missing_info > 0].to_dict()


def get_skew_kurtosis(df):
    num_df = df.select_dtypes(include='number')
    stats = pd.DataFrame()
    stats['Skewness'] = num_df.skew()
    stats['Kurtosis'] = num_df.kurtosis()
    return stats.round(2).to_dict()

def detect_duplicates(df):
    return df.duplicated().sum()

def get_data_summary(df, top_n=5):
    summary=[]
    cat_cols = df.columns
    for col in cat_cols:
        unique_count = df[col].nunique()

        col_data = df[col].dropna()
        total_count = len(col_data)
        if total_count ==0:
            continue
        dtype = str(col_data.dtype)
        mode_value = df[col].mode().iloc[0] if not df[col].mode().empty else None

        value_counts = df[col].value_counts(normalize=True) * 100
        
        cardinality_ratio = unique_count / len(df) if len(df) > 0 else None
        dominance_ratio = value_counts.iloc[0] if not value_counts.empty else None
        entropy_score = entropy(value_counts, base=2) if not value_counts.empty else 0

        summary.append({
           "Column": col,
           "DataType": dtype,
            "Unique Count": unique_count,
            "Mode": mode_value,
            "Cardinality Ratio": round(cardinality_ratio, 4) if cardinality_ratio is not None else None,
            "Dominance Ratio Percent": round(dominance_ratio, 2) if dominance_ratio is not None else None,
            "Entropy Score": round(entropy_score,2) if entropy_score is not None else None
        })
    return summary

def detect_outliers(df):
    outlier_counts = {}
    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        count = df[(df[col] < lower_bound) | (df[col] > upper_bound)].shape[0]
        outlier_counts[col] = int(count)
    return outlier_counts

def perform_eda(df, output_dir="static/charts"):
    os.makedirs(output_dir, exist_ok=True)
    charts = []
    width = 8
    height = 6

    #histplot for Numbered Values
    for col in df.select_dtypes(include="number").columns:
        plt.figure(figsize=(width,height))
        sns.histplot(df[col].dropna(),kde=True)
        plt.title(f"Histogram of {col}")
        chart_name = f"{col}_hist.png"
        chart_path = os.path.join(output_dir,chart_name)
        plt.savefig(chart_path)
        plt.close()
        web_path = f"/static/charts/{chart_name}" 
        charts.append(web_path)
    
    #Pie chart for categorical values 
    for col in df.select_dtypes(include=['object','category']).columns:
        unique_vals = df[col].nunique(dropna=True)
        total_counts = len(df[col].dropna())
        if unique_vals > 20 or unique_vals/total_counts > 0.90:
            continue
        
        value_counts = df[col].value_counts(dropna=True)

        if unique_vals < 10:
            plt.figure(figsize=(width,height))
            df[col].value_counts().plot.pie(
                autopct = '%1.1f%%',
                startangle=90,
                counterclock = False
            )
            plt.ylabel("")
            plt.title(f'Pie Chart for {col}')

        else:
            plt.figure(figsize=(width,height))
            sns.countplot(x=col,data=df)
            plt.ylabel("")
            plt.title(f"Bar Chart of {col}")
            plt.xticks(rotation=45)
        chart_name = f"{col}_cat.png"
        chart_path = os.path.join(output_dir,chart_name)
        plt.tight_layout()
        plt.savefig(chart_path,bbox_inches="tight")
        plt.close()
        web_path= f"/static/charts/{chart_name}"
        charts.append(web_path)
    
    #heatmap for numbered Values
    plt.figure(figsize=(width,height))
    corr = df.select_dtypes(include='number').corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title("Correlation Heatmap")
    heatmap_path = os.path.join(output_dir,"correlation_heatmap.png")
    plt.tight_layout()
    plt.savefig(heatmap_path)
    plt.close
    charts.insert(0,"/static/charts/correlation_heatmap.png")

    numerical_summary = df.describe().T[['count','mean', '50%', 'std', 'min', 'max']]
    numerical_summary.replace([np.inf, -np.inf], np.nan, inplace=True)
    eda_summary = {
        "duplicate_count": sanitize_for_json(detect_duplicates(df)),
        "data_summary":sanitize_for_json(get_data_summary(df)),
        "outlier_summary":sanitize_for_json(detect_outliers(df)),
        "skew_kurt": get_skew_kurtosis(df)
    }
    return numerical_summary.to_dict(), charts, eda_summary

def sanitize_for_json(obj):
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k,v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(i) for i in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj,(np.floating,)):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, float) and(math.isnan(obj) or math.isinf(obj)):
        return None
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    return obj


