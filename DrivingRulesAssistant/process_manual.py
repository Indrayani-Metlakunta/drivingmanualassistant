# import os
# import hashlib
# import PyPDF2
# import sqlite3
# from dotenv import load_dotenv

# # Load API key from .env file (for future GPT-4 usage)
# load_dotenv()

# # Function to extract text from a PDF driving manual
# def extract_text_from_pdf(pdf_path):
#     text = ""
#     with open(pdf_path, 'rb') as file:
#         reader = PyPDF2.PdfReader(file)
#         for page in reader.pages:
#             text += page.extract_text()
#     return text

# # Function to clean and preprocess text
# def clean_text(text):
#     return text.strip().replace('\n', ' ').replace('\r', '')

# # Function to generate a hash for each section (to avoid duplication)
# def generate_hash(text):
#     return hashlib.md5(text.encode()).hexdigest()

# # Initialize the database
# def initialize_db(conn):
#     c = conn.cursor()
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS driving_rules (
#             path TEXT,
#             hash TEXT,
#             rule_text TEXT
#         )
#     ''')
#     conn.commit()

# # Function to extract and store driving rules in the database
# def process_and_store_rules(pdf_path, conn):
#     rule_text = extract_text_from_pdf(pdf_path)
#     cleaned_text = clean_text(rule_text)
#     rule_hash = generate_hash(cleaned_text)
    
#     # Store the rule in the database
#     c = conn.cursor()
#     c.execute("INSERT INTO driving_rules (path, hash, rule_text) VALUES (?, ?, ?)",
#               (pdf_path, rule_hash, cleaned_text))
#     conn.commit()

# # Example usage
# if __name__ == '__main__':
#     conn = sqlite3.connect('driving_rules.db')
#     initialize_db(conn)
#     pdf_path = 'Drivers_Manual_0723_English.pdf'  # Change this to your PDF filename
#     process_and_store_rules(pdf_path, conn)
#     conn.close()
import streamlit as st
import sqlite3
import openai
import os
import pdfplumber
import camelot
from pdf2image import convert_from_path
from dotenv import load_dotenv
from PIL import Image
import io

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Replace with the actual path to your driving rules PDF
pdf_path = "D:\DrivingRulesAssistant\Drivers_Manual_0723_English.pdf"  # <-- Update this path to your actual PDF location

# Function to connect to the SQLite database
def connect_db(db_path='driving_rules.db'):
    return sqlite3.connect(db_path)

# Function to retrieve a relevant driving rule (basic example: we’ll just fetch the first rule)
def get_driving_rule(conn):
    c = conn.cursor()
    c.execute("SELECT rule_text FROM driving_rules LIMIT 1")  # Fetch the first rule (you can improve this to fetch based on query later)
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

# Function to extract text from PDF using pdfplumber
def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text()
    return extracted_text

# Function to extract images from PDF using pdf2image
def extract_images_from_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    image_list = []
    for image in images:
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)
        image_list.append(buf)
    return image_list

# Function to extract tables from PDF using Camelot
def extract_tables_from_pdf(pdf_path):
    tables = camelot.read_pdf(pdf_path, pages='all')
    table_data = [table.df for table in tables]
    return table_data

# Streamlit app
def main():
    st.title("Driving Rules Assistant")
    
    # Connect to the database
    conn = connect_db()

    # Automatically extract data from your existing PDF
    st.subheader("Data Extracted from the Pre-loaded PDF")

    # Extract text
    extracted_text = extract_text_from_pdf(pdf_path)
    st.text_area("Extracted Text", extracted_text, height=300)

    # Extract images
    image_buffers = extract_images_from_pdf(pdf_path)
    st.subheader("Extracted Images")
    for i, buf in enumerate(image_buffers):
        image = Image.open(buf)
        st.image(image, caption=f"Page {i + 1}", use_column_width=True)

    # Extract tables
    tables = extract_tables_from_pdf(pdf_path)
    st.subheader("Extracted Tables")
    for i, table_df in enumerate(tables):
        st.write(f"Table {i + 1}")
        st.write(table_df)

    # User input for the driving rules question
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
