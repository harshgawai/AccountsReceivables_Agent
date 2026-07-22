import os
import gradio as gr
from dotenv import load_dotenv
from operator import itemgetter

from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

DB_PATH = "sqlite:///data/ar_data.db"

def init_agent():
    if not os.environ.get("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY environment variable is not set. Please set it in a .env file.")
    
    # Initialize LLM and DB
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)
    db = SQLDatabase.from_uri(DB_PATH)

    # Generates the raw SQL string
    write_query = create_sql_query_chain(llm, db)
    
    # Executes the string against local sqlite DB
    execute_query = QuerySQLDataBaseTool(db=db)
    

    write_query = create_sql_query_chain(llm, db)
    execute_query = QuerySQLDataBaseTool(db=db)
    
    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question naturally.
        Do not output the raw SQL or reasoning unless explicitly asked.

        Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """
    )
    
    answer_chain = answer_prompt | llm | StrOutputParser()
    
    return write_query, execute_query, answer_chain

try:
    write_query, execute_query, answer_chain = init_agent()
    system_ready = True
except Exception as e:
    system_ready = False
    error_msg = str(e)

def extract_sql(text):
    """Strips Markdown formatting and text prefixes from the LLM's SQL output."""
    text = text.strip()
    if text.startswith("```sql"):
        text = text[6:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
        
    text = text.strip()
    if text.startswith("SQLQuery:"):
        text = text[9:]
        
    return text.strip()

def chat_interface(user_message, history):
    if not system_ready:
        return f"System Initialization Error: {error_msg}. Please fix the error and restart the app."
    
    try:
        # Generate SQL
        raw_query = write_query.invoke({"question": user_message})
        query = extract_sql(raw_query)
        print(f"\n--- New Request ---")
        print(f"Generated SQL: {query}")
        
        # Execute SQL
        result = execute_query.invoke(query)
        print(f"DB Result: {result[:500]}...") # truncate very long outputs
        
        # Format Answer
        final_answer = answer_chain.invoke({
            "question": user_message,
            "query": query,
            "result": result
        })
        return final_answer
    except Exception as e:
        return f"An error occurred while processing your request: {str(e)}"

# Define the Gradio interface
with gr.Blocks(title="AR Collection Copilot", theme=gr.themes.Soft()) as app:
    gr.Markdown("# Accounts Receivable Collection Copilot ")
    gr.Markdown("Ask questions about your customers, invoice statuses, or get recommendations for outreach channels based on past data.")
    
    if not system_ready:
        gr.Markdown(f"**Error initializing pipeline:** {error_msg}")
    
    chatbot = gr.ChatInterface(
        fn=chat_interface,
        examples=[
            "Who are the top 3 customers with the highest total unpaid amount?",
            "Based on past communications, what is the most successful channel to contact CUST_0012?",
            "How many invoices are currently late, and what is their total value?",
            "Which customers require more collections effort and why?"
        ]
    )

if __name__ == "__main__":
    app.launch()
