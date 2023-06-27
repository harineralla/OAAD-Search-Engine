import pandas as pd
import sqlite3

dataframe = pd.read_csv('news_summary1.csv', encoding='unicode_escape', header='infer',usecols=['headlines','url', 'short_description'])

print(dataframe.dtypes)
# Create an in-memory SQLite database
conn = sqlite3.connect(':memory:')

# Store the DataFrame in the database
dataframe.to_sql('data_table', conn, index=False)

# Perform the SQL query on the database
query = "SELECT * FROM data_table WHERE short_description LIKE '%Daman and%'"
query_result = pd.read_sql_query(query, conn)

json_result = query_result.to_json(orient='records')

json_result = json_result.replace('\\/', '/')
# Close the database connection
conn.close()

query_result.to_csv('query_result.csv', index=False)
with open('query_result.json', 'w') as file:
    file.write(json_result)