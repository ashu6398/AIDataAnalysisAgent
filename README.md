# AI Data Analysis Agent

This project is an **Automated Data Analysis & Reporting Agent** built using **Google Generative AI**. 
It is capable of performing **data cleaning**, **exploratory data analysis (EDA)**, and **question answering** 
based on the uploaded dataset.

## Features

- **Data Cleaning Agent** – Automatically detects and handles missing values, duplicates, and formatting issues.
- **EDA Agent** – Generates statistical summaries, visualizations, and trends.
- **Insights Agent** – Allows users to ask natural language questions about the dataset.
- **Modular Agent Design** – Separate Python files for each functionality (`data_cleaner.py`, `eda_agent.py`, `genai_agent.py`).
- **Two-Part Architecture**:
  - **Backend** – Handles agent logic and API calls.
  - **Frontend** – Streamlit UI for interaction.

## Project Structure

```
AIDataAnalysisAgent/
│
├── agents/
│   ├── data_cleaner.py       # Handles data cleaning
│   ├── eda_agent.py          # Performs exploratory data analysis
│   ├── genai_agent.py           # Answers user queries
│
├── static/                   # Static files (if any)
├── .env                      # Stores API keys and environment variables
├── backend.py                # Backend service for AI agents
├── frontend.py               # Streamlit-based frontend
├── requirements.txt          # Required Python packages
└── README.md                 # Project documentation
```

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/AIDataAnalysisAgent.git
cd AIDataAnalysisAgent
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Add Google Generative AI API Key
Create a `.env` file in the project root and add:
```
GOOGLE_API_KEY=your_api_key_here
```

### 5. Run the Backend
```bash
python backend.py
```

### 6. Run the Frontend (Streamlit)
```bash
streamlit run frontend.py
```

## Tech Stack
- **Python**
- **Google Generative AI**
- **Pandas, Matplotlib, Seaborn** (for data analysis & visualization)
- **Streamlit** (for frontend UI)
- **dotenv** (for environment variables)

## Future Enhancements
- Support for larger datasets
- More visualization types
- Model fine-tuning for domain-specific analysis

---
**Author:** Ashutosh  
**License:** MIT
