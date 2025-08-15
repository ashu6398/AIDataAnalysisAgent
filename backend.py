from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
import pandas as pd
from pydantic import BaseModel
from agents import data_cleaner,eda_agent, genai_agent
import uvicorn

#temporary data Storage
data_store = {
    "df": None,
    "clean_df": None,
    "numerical_summary": None,
    "charts": None,
    "eda_summary": None
}

#Helper Functions
def get_df(key="df"):
    df = data_store.get(key)
    if df is None:
        raise HTTPException(status_code=400, detail=f"No data found for {key}")
    return df

#Pydantic Models
class CleaningRequest(BaseModel):
    cleaning_plan: dict

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type != "text/csv":
            raise HTTPException(status_code=400, detail="Only CSV Files allowed.")
    try:
        df = pd.read_csv(file.file)
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Invalid CSV or contains no columns")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    if df.empty:
        raise HTTPException(status_code=400, detail="CSV is empty or malformed.")
    data_store['df'] = df
    data_store['clean_df'] = df.copy()

    eda_required , reason = eda_agent.needs_eda(df)
    missing_columns = eda_agent.get_missing_columns(df)
    return {"message": "File uploaded successfully",
            "columns": df.columns.tolist(),
            "shape":df.shape,
            "eda_required":eda_required,
            "reason":reason,
            "missing_columns": missing_columns
            }


@app.post("/clean")
def clean_csv(request : CleaningRequest):
    df = data_store["df"]
    df_clean, audit_logs = data_cleaner.clean_data(df, request.cleaning_plan)
    data_store['clean_df']= df_clean
    return {"message": "Missing values cleaned successully", "audit_log": audit_logs}
    
@app.get("/get_clean_data")
def get_clean_data():
    df = data_store['clean_df']
    return df.to_dict(orient="records")
    
@app.get("/eda")
def eda():
    df = data_store['clean_df']
    df = data_cleaner.check_for_date(df)  
    numerical_summary, charts , eda_summary = eda_agent.perform_eda(df)
    
    data_store['numerical_summary'] = numerical_summary
    data_store['charts'] = charts
    data_store['eda_summary'] = eda_summary
    numerical_summary = eda_agent.sanitize_for_json(numerical_summary)
    return {
        "numerical_summary":numerical_summary,
            "charts":charts,
            "eda_summary":eda_summary
            }

@app.get("/ask")
def ask():
    if not data_store.get("numerical_summary") or not data_store.get("eda_summary"):
        raise HTTPException(status_code=400, detail= "EDA must be run to generate Insights")
    eda_summary = str(data_store['numerical_summary']) + str(data_store['eda_summary'])
    response = genai_agent.get_insights(eda_summary)
    return {'answer': response}

app.mount("/static",StaticFiles(directory="static"),name="static")

if __name__ == '__main__':
    uvicorn.run("backend:app",reload=True)