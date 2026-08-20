# 🤖 DataWhisperer

DataWhisperer is an AI-powered analytics tool that lets you upload your data and get answers in plain English. Instead of writing complex SQL queries or code, you can simply ask questions, and the application will generate interactive visualizations and insights for you.

This application uses a local Large Language Model (LLM) via Ollama, PySpark for data processing, and Panel for the interactive web dashboard.

## ✨ Core Features

  * **File Upload:** Load your data directly into the app. Supports `.csv`, `.xlsx` and `.xls` files.
  * **Natural Language Queries:** Ask questions in plain English, like "What are the top 10 products by sales?" or "Show me the monthly revenue trend."
  * **AI-Powered SQL Generation:** Uses an LLM (e.g., `gemma3`) and LangChain to automatically convert your question into an optimized Spark SQL query.
  * **Smart Visualization:** A second AI agent analyzes your query and the SQL results to recommend the best visualization (bar chart, pie chart, line chart, KPI, etc.).
  * **Interactive Dashboards:** All charts are rendered with Plotly and are fully interactive (hover, zoom, pan).
  * **Spark-Powered:** Leverages the PySpark engine to handle data processing, enabling it to work with larger-than-memory datasets (though it's configured for local mode by default).
  * **Self-Correcting SQL:** If a generated SQL query fails, an AI-powered debugger chain attempts to fix the query and retry.

## 🚀 How It Works

DataWhisperer uses a multi-step AI chain to turn your question into a chart:

1.  **Upload:** You upload a data file. The app uses Pandas to quickly read the file and then creates a PySpark DataFrame and a temporary SQL view.
2.  **Ask:** You ask a question in the text box, e.g., "Count customers by region and show as a pie chart."
3.  **NL-to-SQL:** The app sends your question, the data's schema, and some sample rows to an LLM with a specialized "SQL Expert" prompt. The LLM generates a Spark SQL query.
4.  **Execute:** The generated SQL is run against the PySpark DataFrame.
5.  **Recommend Viz:** The original question, the SQL query, and a preview of the results are sent to a "Visualization Expert" AI prompt. This AI recommends the best chart type and configuration (e.g., `{"visualization_type": "pie", "title": "Customer Distribution by Region", ...}`). It also honors explicit requests like "show as a pie chart."
6.  **Render:** The `VisualizationEngine` uses Plotly and Panel to build and display the recommended interactive chart in the dashboard.

## 🛠️ Tech Stack

  * **Data Processing:** `pyspark`, `pandas`, `pyarrow`
  * **Web Framework & UI:** `panel`
  * **Visualization:** `plotly`, `bokeh`
  * **LLM Integration:** `langchain`, `langchain-openai` (used to connect to any OpenAI-compatible API, including Ollama)
  * **File Handling:** `openpyxl`, `xlrd`
  * **Configuration:** `python-dotenv`

## Prerequisites: Run a Local LLM

This project is configured to use a local LLM served by **Ollama**.

1.  **Install Ollama:** Download and install it from [ollama.com](https://ollama.com/).
2.  **Pull the model:** The local configuration now points to `gemma3`, so pull it once:
    ```sh
    ollama pull gemma3
    ```
3.  **Start Ollama** if it is not already running.

## ⚙️ Setup and Installation

1.  **Clone the repository:**

    ```sh
    git clone <your-repo-url>
    cd data-whisperer
    ```

2.  **Create and activate a virtual environment:**

    ```sh
    # Windows
    python -m venv myenv
    myenv\Scripts\activate.bat

    # macOS / Linux
    python3 -m venv myenv
    source myenv/bin/activate
    ```

3.  **Install the required dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file:**
    Create a file named `.env` in the root of the project directory to configure your settings. The application loads this file automatically at startup.

    ```ini
    # .env
    # Ollama example
    DATAWHISPERER_LLM_URL=http://localhost:11434/v1
    DATAWHISPERER_LLM_MODEL=gemma3
    DATAWHISPERER_LLM_API_KEY=ollama

    # Set the port for the Panel app
    DATAWHISPERER_PORT=5007
    ```

## 🚀 Running the Application

1.  **Activate the existing environment**:

    ```sh
    myenv\Scripts\activate
    ```

2.  **Run the `main.py` script:**

    ```sh
    python main.py
    ```

    The app now prefers the Spark distribution bundled with `pyspark`, so it avoids conflicts with a machine-wide Spark install.

    Make sure Ollama is running locally before you start asking questions in the app.

3.  **Open the application:**
    The console will log the URL. By default, it is:
    **[http://localhost:5007](https://www.google.com/search?q=http://localhost:5007)**

You can now upload a file, ask questions, and see the results\!

## 📂 Project Structure

```
/
├── main.py             # Main application entry point that starts the Panel server
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
└── src/
    ├── config.py           # Dataclass for all application configuration
    ├── data/
    │   └── data_loader.py    # (Legacy/Alternative) Spark-native data loader
    ├── query/
    │   └── query_processor.py # Core AI logic: NL-to-SQL, SQL-to-Viz
    ├── ui/
    │   └── dashboard.py     # Panel dashboard UI components and layout
    ├── utils/
    │   └── logger.py        # Logging setup
    └── visualization/
        └── viz_engine.py      # Creates Plotly charts from data + config
```

## 🔧 Configuration

All settings are managed in `src/config.py` and can be overridden with environment variables (as shown in the `.env` file setup).

Key settings you might want to change:

  * `llm_model`: The Ollama model to use locally (for example `gemma3`, `llama3`, or `mistral`).
  * `llm_base_url`: The API endpoint for your LLM.
  * `port`: The port to run the web server on.
  * `supported_file_types`: List of allowed file extensions.
  * `max_retries`: Number of times the AI should try to fix a broken SQL query.
