import sys
import os
import pandas as pd
import sqlite3
from django.shortcuts import render
from django.views import View
from adminapp.models import QueryResult



def index(request):
    return render(request, "index.html")


class SearchView(View):
    template_name = 'search.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        keyword = request.POST.get('searchInput')
        search_type = request.POST.get('search_type')


        csv_path = os.path.join(os.path.dirname(__file__), 'news_summary1.csv')
        dataframe = pd.read_csv(csv_path, encoding='unicode_escape', header='infer', usecols=['headlines', 'url', 'short_description'])
        # dataframe = pd.read_csv('news_summary1.csv', encoding='unicode_escape', header='infer', usecols=['headlines', 'url', 'short_description'])

        conn = sqlite3.connect(':memory:')
        dataframe.to_sql('data_table', conn, index=False)

        # breakpoint()
        if search_type == 'AND':
            values = keyword.split()
            conditions = " AND ".join(["short_description LIKE ?"] * len(values))
            query = f"SELECT * FROM data_table WHERE {conditions}"
            query_values = tuple(f'%{value}%' for value in values)
        elif search_type == 'OR':
            values = keyword.split()
            conditions = " OR ".join(["short_description LIKE ?"] * len(values))
            query = f"SELECT * FROM data_table WHERE {conditions}"
            query_values = tuple(f'%{value}%' for value in values)
        else:
            values = keyword.split()
            conditions = "".join(["short_description LIKE ?"] * len(values))
            query = f"SELECT * FROM data_table WHERE {conditions}"
            query_values = tuple(f'%{value}%' for value in values)

        query_result = pd.read_sql_query(query, conn, params=query_values)

        query_result_dict = query_result.to_dict('records')  # Convert the DataFrame to a list of dictionaries
        query_result_objs = [
            QueryResult(
                headings=row['headlines'],
                short_description=row['short_description'],
                url=row['url']
            )
            for row in query_result_dict
        ]  # Create QueryResult objects for each record

        QueryResult.objects.bulk_create(query_result_objs)  # Save all QueryResult objects in a single database query

        conn.close()

        return render(request, self.template_name, {'query_result': query_result})
