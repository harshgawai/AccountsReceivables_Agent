# Accounts Receivable Agent

A conversational AI agent designed to act as a "Collection Copilot" for Accounts Receivable teams. This project uses synthetic data that mirrors real-world patterns (like the IBM Late Payment Histories dataset) combined with simulated CRM interaction logs.

The copilot is built using **LangChain** and **Gradio**, utilizing an SQL Agent to query the underlying customer, invoice, and communication data.

## Features
- **Data Generator:** Generates realistic local-business AR data (`generate_dataset.py`).
- **Database Ingestion:** Converts CSVs to an SQLite database for reliable LLM relational querying (`setup_db.py`).
- **Conversational UI:** A Gradio web interface to chat with your data and get recommendations (`app.py`).

## Getting Started

### Prerequisites
- Python 3.9+
- A Google API Key for Gemini (or modify `app.py` to use OpenAI)

### Installation
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd AR_Recommendation_Agent
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory and add your API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

### Usage
1. **Generate the synthetic data:**
   ```bash
   python generate_dataset.py
   ```
2. **Setup the SQLite database:**
   ```bash
   python setup_db.py
   ```
3. **Run the Gradio Application:**
   ```bash
   python app.py
   ```
