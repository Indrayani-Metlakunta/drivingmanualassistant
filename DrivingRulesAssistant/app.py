# # import streamlit as st
# # import sqlite3
# # import os
# # import openai
# # from dotenv import load_dotenv

# # # Load API key from .env file
# # load_dotenv()
# # openai.api_key = os.getenv("OPENAI_API_KEY")

# # # Function to connect to the SQLite database
# # def connect_db(db_path='driving_rules.db'):
# #     return sqlite3.connect(db_path)

# # # Function to retrieve a relevant driving rule (basic example: we’ll just fetch the first rule)
# # def get_driving_rule(conn):
# #     c = conn.cursor()
# #     c.execute("SELECT rule_text FROM driving_rules LIMIT 1")  # Fetch the first rule (you can improve this to fetch based on query later)
# #     row = c.fetchone()
# #     return row[0] if row else None

# # # Function to use GPT-4 to generate a response based on a user question and a rule

# # def summarize_and_answer_question(rule_text, user_question):
# #     messages = [
# #         {
# #             "role": "system",
# #             "content": "You are an assistant tasked with answering questions about driving rules and regulations based on a comprehensive driving manual."
# #         },
# #         {
# #             "role": "user",
# #             "content": f"""
# #             The user has asked: {user_question}
# #             The relevant driving rule is as follows: {rule_text}
# #             Please provide a clear and concise answer based on the provided driving rule.
# #             """
# #         }
# #     ]

# #     response = openai.ChatCompletion.create(
# #         model="gpt-4",
# #         messages=messages,
# #         max_tokens=1000,
# #         temperature=0.1
# #     )

# #     return response.choices[0].message.content.strip()

# # # Streamlit app
# # def main():
# #     st.title("Driving Rules Assistant")
    
# #     # Connect to the database
# #     conn = connect_db()
    
# #     # User input
# #     user_query = st.text_input("Ask a question about driving rules:")
    
# #     if st.button("Get Answer"):
# #         if user_query:
# #             # Fetch a relevant rule from the database (currently fetching first rule)
# #             relevant_rule = get_driving_rule(conn)
            
# #             if relevant_rule:
# #                 # Use GPT-4 to summarize and answer based on the rule and user query
# #                 answer = summarize_and_answer_question(relevant_rule, user_query)
# #                 st.write(f"Answer: {answer}")
# #             else:
# #                 st.warning("No rules found in the database.")
# #         else:
# #             st.warning("Please enter a question.")

# # if __name__ == '__main__':
# #     main()
# import streamlit as st
# import sqlite3
# import openai
# import os
# from dotenv import load_dotenv

# # Load API key from .env file
# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

# # Function to connect to the SQLite database
# def connect_db(db_path='driving_rules.db'):
#     return sqlite3.connect(db_path)

# # Function to retrieve a relevant driving rule (basic example: we’ll just fetch the first rule)
# def get_driving_rule(conn):
#     c = conn.cursor()
#     c.execute("SELECT rule_text FROM driving_rules LIMIT 1")  # Fetch the first rule (you can improve this to fetch based on query later)
#     row = c.fetchone()
#     return row[0] if row else None

# # Function to use GPT-4 to generate a response based on a user question and a rule
# def summarize_and_answer_question(rule_text, user_question):
#     # Truncate the rule text to prevent exceeding the token limit
#     max_rule_length = 3000  # Set a reasonable limit to avoid hitting token limits
#     truncated_rule_text = rule_text[:max_rule_length]  # Truncate the rule text if it's too long

#     messages = [
#         {
#             "role": "system",
#             "content": "You are an assistant tasked with answering questions about driving rules and regulations based on a comprehensive driving manual."
#         },
#         {
#             "role": "user",
#             "content": f"""
#             The user has asked: {user_question}
#             The relevant driving rule is as follows: {truncated_rule_text}
#             Please provide a clear and concise answer based on the provided driving rule.
#             """
#         }
#     ]

#     # OpenAI API call, limiting the response tokens
#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=messages,
#         max_tokens=1000,  # Limit the response to avoid large token count
#         temperature=0.1
#     )

#     return response.choices[0]['message']['content'].strip()

# # Streamlit app
# def main():
#     st.title("Driving Rules Assistant")
    
#     # Connect to the database
#     conn = connect_db()
    
#     # User input
#     user_query = st.text_input("Ask a question about driving rules:")
    
#     if st.button("Get Answer"):
#         if user_query:
#             # Fetch a relevant rule from the database (currently fetching first rule)
#             relevant_rule = get_driving_rule(conn)
            
#             if relevant_rule:
#                 # Use GPT-4 to summarize and answer based on the rule and user query
#                 answer = summarize_and_answer_question(relevant_rule, user_query)
#                 st.write(f"Answer: {answer}")
#             else:
#                 st.warning("No rules found in the database.")
#         else:
#             st.warning("Please enter a question.")

# if __name__ == '__main__':
#     main()

import streamlit as st
import sqlite3
import openai
import os
import pdfplumber
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Replace with the actual path to your driving rules PDF
pdf_path = "D:/DrivingRulesAssistant/Manual/manual.pdf"  # <-- Update this path to your actual PDF location

# Function to connect to the SQLite database
def connect_db(db_path='driving_rules.db'):
    return sqlite3.connect(db_path)

# Function to create a table for driving rules in the database
def create_table(conn):
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS driving_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_text TEXT
        )
    ''')
    conn.commit()

# Function to extract text from PDF using pdfplumber and store in the database
def extract_and_store_rules(conn, pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                c = conn.cursor()
                c.execute("INSERT INTO driving_rules (rule_text) VALUES (?)", (text,))
                conn.commit()

# Function to retrieve a relevant driving rule (fetch the first rule)
def get_driving_rule(conn):
    c = conn.cursor()
    c.execute("SELECT rule_text FROM driving_rules LIMIT 1")  # Fetch the first rule (can be improved to fetch by query)
    row = c.fetchone()
    return row[0] if row else None

# Function to use GPT-4 to generate a response based on a user question and a rule
def summarize_and_answer_question(rule_text, user_question):
    # Truncate the rule text to prevent exceeding the token limit
    max_rule_length = 3000  # Set a reasonable limit to avoid hitting token limits
    truncated_rule_text = rule_text[:max_rule_length]  # Truncate the rule text if it's too long

    messages = [
        {
            "role": "system",
            "content": "You are an assistant tasked with answering questions about driving rules and regulations based on a comprehensive driving manual."
        },
        {
            "role": "user",
            "content": f"""
            The user has asked: {user_question}
            The relevant driving rule is as follows: {truncated_rule_text}
            Please provide a clear and concise answer based on the provided driving rule.
            """
        }
    ]

    # OpenAI API call, limiting the response tokens
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1000,  # Limit the response to avoid large token count
        temperature=0.1
    )

    return response.choices[0]['message']['content'].strip()

# Streamlit app
def main():
    st.title("Driving Rules Assistant")
    
    # Connect to the database
    conn = connect_db()
    
    # Create table for storing driving rules
    create_table(conn)
    
    # Extract driving rules from PDF and store in the database (this can be done once)
    if st.button("Extract Rules from PDF"):
        extract_and_store_rules(conn, pdf_path)
        st.success("Rules extracted and stored in the database.")
    
    # User input
    user_query = st.text_input("Ask a question about driving rules:")
    
    if st.button("Get Answer"):
        if user_query:
            # Fetch a relevant rule from the database (currently fetching first rule)
            relevant_rule = get_driving_rule(conn)
            
            if relevant_rule:
                # Use GPT-4 to summarize and answer based on the rule and user query
                answer = summarize_and_answer_question(relevant_rule, user_query)
                st.write(f"Answer: {answer}")
            else:
                st.warning("No rules found in the database.")
        else:
            st.warning("Please enter a question.")

if __name__ == '__main__':
    main()
