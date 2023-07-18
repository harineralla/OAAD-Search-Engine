import os
import re
import pandas as pd
import sqlite3
from django.shortcuts import render
from django.views import View
from adminapp.models import QueryResult
from django.http import JsonResponse
from django.db.models import Q
from adminapp.models import QueryResult

global keyword_results


def is_valid_url(url):
    # Check if the URL matches the specified pattern
    pattern = r'^((http://|https://)?(www\.)?[a-zA-Z0-9]+\.)(edu|com|org|net|gov)$'
    return bool(re.match(pattern, url))


def index(request):
    return render(request, "index.html")


class SearchView(View):
    template_name = 'search.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        keywords = request.POST.get('searchInput')
        search_type = request.POST.get('search_type')
        # New - Get the sort_by parameter
        sort_by = request.POST.get('sort_by')

        csv_path = os.path.join(os.path.dirname(__file__), 'news_summary1.csv')
        dataframe = pd.read_csv(csv_path, encoding='unicode_escape', header='infer', usecols=[
                                'headlines', 'url', 'short_description'])
        # dataframe = pd.read_csv('news_summary1.csv', encoding='unicode_escape', header='infer', usecols=['headlines', 'url', 'short_description'])

        conn = sqlite3.connect(':memory:')
        dataframe.to_sql('data_table', conn, index=False)

        # Clear the database before adding new search results
        QueryResult.objects.all().delete()

        if search_type == 'AND':
            values = keywords.split(" ")
            conditions = " AND ".join(
                ["short_description LIKE ?"] * len(values))
            query = f"SELECT * FROM data_table WHERE {conditions}"
            query_values = tuple(f'%{value}%' for value in values)
        elif search_type == 'OR':
            values = keywords.split(" ")
            conditions = " OR ".join(
                ["short_description LIKE ?"] * len(values))
            query = f"SELECT * FROM data_table WHERE {conditions}"
            query_values = tuple(f'%{value}%' for value in values)
        elif search_type == "NOT":
            values = keywords.split(" ")
            conditions = " AND ".join(
                ["short_description NOT LIKE ?"] * len(values))
            query = f"SELECT * FROM data_table WHERE {conditions}"
            query_values = tuple(f'%{value}%' for value in values)
        else:
            values = keywords.split(" ")
            conditions = " AND ".join(
                ["short_description LIKE ?"] * len(values))
            query = f"SELECT * FROM data_table WHERE {conditions}"
            query_values = tuple(f'%{value}%' for value in values)

        query_result = pd.read_sql_query(query, conn, params=query_values)

        # Convert the DataFrame to a list of dictionaries
        query_result_dict = query_result.drop_duplicates(subset=['headlines']).to_dict('records')
        # query_result_dict = query_result.to_dict('records')
        query_result_objs = [
            QueryResult(
                headlines=row['headlines'],
                short_description=row['short_description'],
                url=row['url']
            )
            for row in query_result_dict
        ]  # Create QueryResult objects for each record

        # Save all QueryResult objects in a single database query
        QueryResult.objects.bulk_create(query_result_objs)

        query_result_objs = QueryResult.objects.all()

        # Retrieve the values from QueryResult objects
        query_result_values = list(query_result_objs.values(
            'headlines', 'url', 'short_description'))

        # Convert the list of dictionaries to a DataFrame
        query_results = pd.DataFrame(query_result_values)[1:]

        global keyword_results

        keyword_results = query_result_objs

        conn.close()

        return render(request, self.template_name, {
            'total_results': len(query_result_objs),
            'query_result': query_results})

    def sort_query_results(request):
        global keyword_results
        sort_by = request.POST.get("sort_by")

        if sort_by == 'alphabetical':
            query_result_objs = QueryResult.objects.order_by('headlines')
        else:
            # Default sorting (no specific order)
            query_result_objs = QueryResult.objects.all()

        query_result_values = list(query_result_objs.values(
            'headlines', 'url', 'short_description'))

        # Convert the list of dictionaries to a DataFrame
        query_results = pd.DataFrame(query_result_values)[1:]

        return render(request, 'search.html', {
            'total_results': len(query_result_objs),
            'query_result': query_results})
