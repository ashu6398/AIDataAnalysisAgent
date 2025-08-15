import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

def get_insights(eda_summary):
    prompt_insights = f"""You are an expert data analyst. I will give you an EDA result in structured text format. Summarize it concisely in bullet points focusing only on the most important and actionable findings.
        Avoid introductory phrases like “Here are the key insights.
        Remove repetitive or obvious details
        Combine related points into one where possible
        Keep each bullet under 20 words
        Prioritize trends, anomalies, correlations, and unique data characteristics
        Output only the bullet list
        After the summary, add a section titled:
        "Further Points to Analyze:"
        Suggest 5 additional areas to investigate based on the data, trends, or anomalies found
        Keep each suggestion short and actionable
    {eda_summary}
    """
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt_insights
    )

    return response.text
    


