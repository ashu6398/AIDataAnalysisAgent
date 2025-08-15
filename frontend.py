import streamlit as st
import pandas as pd
import requests
from io import BytesIO

BASE_URL = "http://127.0.0.1:8000"

# ----- Streamlit Page Config -----
st.set_page_config("AI Data Analyst",layout="wide")
st.title("AI Data Analysis Assistant")

# ----- Session State Defaults -----
defaults = {
    "cleaned": False,
    "cleaned_df": None,
    "audit_logs": None,
    "run_eda": False
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ----- Helper Functions -----
def safe_json(res):
    """Safely decode JSON from response."""
    try:
        return res.json()
    except Exception:
        st.error("Invalid JSON response from server")
        return None
    
def chunk_list(lst, n):
    """Split a list into chunks of size n."""
    return [lst[i:i+n] for i in range(0, len(lst), n)]

# ----- File Upload -----
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    st.success("CSV uploaded.")

    file_bytes = uploaded_file.read()
    buffer = BytesIO(file_bytes)
    df = pd.read_csv(buffer)
    st.session_state['original_df'] = df      #Saving original for Comparision

    #send file to backend
    buffer.seek(0)
    files = {"file": (uploaded_file.name, buffer, "text/csv")} 
    res = requests.post(f"{BASE_URL}/upload",files=files)
    df_info = safe_json(res)

    if not df_info:
        st.stop()

    if not (st.session_state.run_eda or st.session_state.cleaned):
        st.subheader("Data Preview: ")
        st.dataframe(df.head())
        
    #Handling missing Values 
    missing_columns = df_info.get("missing_columns", {})

    if missing_columns and not st.session_state.cleaned:
        cleaning_plan= {}
        st.warning("Missing Values found. Choose handeling method:")
        for col in missing_columns:
            method = st.selectbox(f"{col} - {missing_columns[col]} missing values",
                                ["mean","median","mode","drop"],
                                key=f"clean_method_{col}")
            cleaning_plan[col] = method

        if st.button("Apply Cleaning Method"):
            clean_res = requests.post(f"{BASE_URL}/clean", json={"cleaning_plan":cleaning_plan})
            response_data = safe_json(clean_res)
            if not response_data:
                st.error("Cleaning Failed")
                st.stop()
                
            st.success("Data Cleaned Successfully")
            st.session_state.cleaned = True
            st.session_state.audit_logs = response_data.get("audit_log",[])
                        
            #Fetch Clean Data
            cleaned_df_res = requests.get(f"{BASE_URL}/get_clean_data")
            cleaned_data = safe_json(cleaned_df_res)
            if cleaned_data:
                    st.session_state.cleaned_df = pd.DataFrame(cleaned_df_res.json())
                    st.success("Fetched Cleaned Data Successfully")
                    st.rerun()
        
    #Showing Clean Data
    if st.session_state.cleaned and st.session_state.cleaned_df is not None and not st.session_state.get("run_eda", False):
        st.subheader("Cleaned Data Preview:")
        st.dataframe(st.session_state.cleaned_df.head())
        #Show Audit Logs
        if st.session_state.audit_logs:
            with st.expander("View Cleaning Audit Logs"):
                for log in st.session_state.audit_logs:
                        st.write(f" - {log}")

    if st.button("Run EDA"):
        st.session_state.run_eda = True
        with st.spinner("Analyzing Data ... "):
            eda_res = requests.get(f"{BASE_URL}/eda")
            eda_response = safe_json(eda_res)
            if not eda_response:
                st.stop()
            st.write(f"**Number of Rows:** {df_info['shape'][0]}")
            st.write(f"**Number of Columns:** {df_info['shape'][1]}")
            
            numerical_summary_df = pd.DataFrame(eda_response['numerical_summary'])
            eda_summary = eda_response['eda_summary']
            st.write(f"**Number of duplicate Rows:** {eda_summary['duplicate_count']}")
            
            st.subheader("Data Summary:")
            st.dataframe(eda_summary['data_summary'])

            outlier_data = pd.DataFrame(
                data = eda_summary['outlier_summary'].values(),
                index = eda_summary['outlier_summary'].keys(),
                columns=["Outliers"]
            )
            
            st.subheader("Metrics for Numerical data: ")
            st.dataframe(numerical_summary_df)
            st.dataframe(pd.DataFrame(eda_summary['skew_kurt']).merge(outlier_data,left_index=True,right_index=True))
        
            st.subheader('Generated Charts:')                      
            for group in chunk_list(eda_response['charts'],3):
                cols = st.columns(3)
                for i, chart_path in enumerate(group):
                    if chart_path:
                        cols[i].image(f"{BASE_URL}{chart_path}", use_container_width=True)

            #AI Insights
            with st.spinner("Generating AI Insights...",width="content"):
                ins_res = requests.get(f"{BASE_URL}/ask")
                ins_data = safe_json(ins_res)
                if ins_data:
                    answer = ins_data.get("answer"," No response recieved")
                    st.subheader("AI Insights: ")
                    st.write(answer)
