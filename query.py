import sys
import pandas as pd
import sqlite3

dataframe = pd.read_csv('news_summary1.csv', encoding='unicode_escape', header='infer', usecols=['headlines', 'url', 'short_description'])

print(dataframe.dtypes)

# Create an in-memory SQLite database
conn = sqlite3.connect(':memory:')

# Store the DataFrame in the database
dataframe.to_sql('data_table', conn, index=False)

# Check if the correct number of arguments is provided
if len(sys.argv) < 3:
    print("Usage: python script.py values search_type")
    sys.exit(1)

values = sys.argv[1].split()
search_type = sys.argv[2].upper()

# Check the search type and build the appropriate query
if search_type == 'AND':
    conditions = " AND ".join(["short_description LIKE ?"] * len(values))
    query = f"SELECT * FROM data_table WHERE {conditions}"
    query_values = tuple(f'%{value}%' for value in values)
elif search_type == 'OR':
    conditions = " OR ".join(["short_description LIKE ?"] * len(values))
    query = f"SELECT * FROM data_table WHERE {conditions}"
    query_values = tuple(f'%{value}%' for value in values)
else:
    print("Invalid search type. Available search types: AND, OR, NOT")
    sys.exit(1)

# Execute the query and fetch the results
query_result = pd.read_sql_query(query, conn, params=query_values)

# Convert the query results to JSON
json_result = query_result.to_json(orient='records')

# Correct the forward slash in the JSON result
json_result = json_result.replace('\\/', '/')

# Close the database connection
conn.close()

# Save the query results to CSV
query_result.to_csv('query_result.csv', index=False)

# Save the query results to JSON
with open('query_result.json', 'w') as file:
    file.write(json_result)
