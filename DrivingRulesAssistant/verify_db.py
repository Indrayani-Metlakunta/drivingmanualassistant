# import sqlite3

# # Function to connect to the SQLite database and retrieve all stored rules
# def check_db_content():
#     # Connect to the database
#     conn = sqlite3.connect('driving_rules.db')
#     c = conn.cursor()
    
#     # Check if there are any rows in the database
#     c.execute("SELECT COUNT(*) FROM driving_rules")
#     count = c.fetchone()[0]
    
#     if count == 0:
#         print("No rules were found in the database.")
#     else:
#         print(f"{count} rules found in the database.")
    
#     # Close the connection
#     conn.close()

# if __name__ == '__main__':
#     check_db_content()
import sqlite3

# Function to retrieve and print all rules from the database
def print_all_rules():
    conn = sqlite3.connect('driving_rules.db')
    c = conn.cursor()
    
    # Retrieve all driving rules from the table
    c.execute("SELECT rule_text FROM driving_rules")
    rows = c.fetchall()
    
    # Print each rule
    for idx, row in enumerate(rows):
        print(f"Rule {idx + 1}:")
        print(row[0])
        print("\n" + "-" * 50 + "\n")
    
    conn.close()

if __name__ == '__main__':
    print_all_rules()
