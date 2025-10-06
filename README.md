<<<<<<< HEAD
# InsightMesh-A-Multi-Agent-Business-Intelligence-Engine
=======
# InsightMesh: Multi-Agent Business Intelligence Engine

InsightMesh is a modern, multi-agent business intelligence application powered by LLMs and Streamlit. It enables users to ask natural language questions about their data and receive instant answers and visualizations.

## Features

- Conversational BI: Ask questions in plain English and get answers with charts.
- Modern UI: Clean, focused interface with only the latest Q&A and graph.
- Multi-Agent Backend: SQL and Pandas agents for flexible data analysis.
- Secure: Sensitive files and credentials are excluded from version control.

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd cypher_KABI_v2
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   - Copy `.env.example` to `.env` and fill in your Anthropic API key and other configs.
4. **Run the backend API:**
   ```bash
   uvicorn app.app:app --reload --port 8000
   ```
5. **Launch the Streamlit UI:**
   ```bash
   streamlit run streamlit_app.py
   ```

## Folder Structure

- `app/` - Backend FastAPI app and agent logic
- `streamlit_app.py` - Streamlit UI
- `requirements.txt` - Python dependencies
- `dummy_employee_financial_data.csv` - Example data

## Environment Variables

Create a `.env` file with:

```
ANTHROPIC_API_KEY=your_key_here
CSV_FILE_PATH=./dummy_employee_financial_data.csv
DATABASE_FILE_PATH=./dummy_employee_financial_data.db
```

## License

MIT License

---

Built for Accel-Anthropic AI Dev Day Hackathon.

# cypher Business Insights Lite

An AI-powered business analytics platform that allows users to query their business data using natural language and get instant insights with visualizations.

## Features

- 🤖 **Natural Language Queries**: Ask business questions in plain English
- 📊 **AI-Powered Analytics**: Automated data analysis and insights generation
- 📈 **Dynamic Visualizations**: Interactive charts and graphs
- 🎨 **cypher Branded UI**: Professional interface with cypher corporate identity
- ⚡ **Real-time Processing**: Instant results from your data

## Getting Started

### Prerequisites

- Python 3.12 or higher
- All dependencies listed in `requirements.txt`

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### Method 1: Using the Streamlit UI (Recommended)

1. **Start the FastAPI Backend Server:**
   ```bash
   python main.py
   ```
   The API server will start on `http://localhost:8000`

2. **Start the Streamlit UI:**
   ```bash
   # Using PowerShell script
   .\start_ui.ps1
   
   # Or using batch file
   .\start_ui.bat
   
   # Or directly with streamlit
   streamlit run streamlit_app.py
   ```
   The UI will be available at `http://localhost:8501`

#### Method 2: Using the API Directly

You can also interact with the FastAPI backend directly:
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`
- Chat Endpoint: `POST http://localhost:8000/api/chat`

### Usage

1. Open the Streamlit UI in your browser
2. Ensure the backend API is connected (green status indicator)
3. Enter natural language questions about your business data
4. View AI-generated insights and visualizations

### Sample Questions

- "Show me the total sales by region"
- "What are the top 5 performing products?"
- "Analyze the revenue trend over the last 12 months"
- "Compare performance between different departments"

## Architecture

- **Backend**: FastAPI with AI/ML capabilities for data analysis
- **Frontend**: Streamlit with custom cypher branding
- **Data Processing**: Pandas, SQLAlchemy for data manipulation
- **AI Engine**: OpenAI integration for natural language processing
- **Visualization**: Plotly for interactive charts 

# Contribute
TODO: Explain how other users and developers can contribute to make your code better. 

...existing code...
- [ASP.NET Core](https://github.com/aspnet/Home)
- [Visual Studio Code](https://github.com/Microsoft/vscode)
- [Chakra Core](https://github.com/Microsoft/ChakraCore)
>>>>>>> 7770a8b (Initial commit: Cleaned for GitHub)
