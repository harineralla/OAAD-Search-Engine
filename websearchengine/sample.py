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


def is_valid_url(url):
    # Check if the URL matches the specified pattern
    pattern = r'^((http://|https://)?(www\.)?[a-zA-Z0-9]+\.)(edu|com|org|net|gov)$'
    return bool(re.match(pattern, url))


def index(request):
    return render(request, "index.html")


def perform_search(query_values, conditions):
    csv_path = os.path.join(os.path.dirname(__file__), 'news_summary1.csv')
    dataframe = pd.read_csv(csv_path, encoding='unicode_escape', header='infer', usecols=[
                            'headlines', 'url', 'short_description'])
    conn = sqlite3.connect(':memory:')
    dataframe.to_sql('data_table', conn, index=False)

    query = f"SELECT * FROM data_table WHERE {conditions}"
    query_result = pd.read_sql_query(query, conn, params=query_values)

    # Convert the DataFrame to a list of dictionaries
    query_result_dict = query_result.to_dict('records')
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

    # Close the connection
    conn.close()

    return query_result_objs


class SearchView(View):
    template_name = 'search.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        keywords = request.POST.getlist('searchInput')
        search_type = request.POST.get('search_type')

        # New - Get the page number from the request
        page_number = request.POST.get('page')

        # Perform the search
        conditions = None
        for keyword in keywords:
            if search_type == 'AND':
                operator = "AND"
                condition = f"short_description LIKE ?"
            elif search_type == 'OR':
                operator = "OR"
                condition = f"short_description LIKE ?"
            elif search_type == "NOT":
                operator = "AND"
                condition = f"NOT short_description LIKE ?"
            else:
                operator = "AND"
                condition = f"short_description LIKE ?"

            keyword_condition = f"{operator} {condition}"
            query_values = tuple(f'%{keyword}%' for keyword in keywords)
            if conditions is None:
                conditions = keyword_condition
            else:
                conditions += f" {keyword_condition}"

        # Perform the search and get the results
        query_result_objs = perform_search(query_values, conditions)

        # Retrieve autocomplete suggestions from the database based on the keyword
        suggestions = QueryResult.objects.filter(
            Q(headlines__in=keywords) | Q(
                short_description__in=keywords)
        ).values_list('headlines', flat=True)[:5]

        autocomplete_suggestions = list(suggestions)

        return render(request, self.template_name, {
            'total_results': len(query_result_objs),
            'autocomplete_suggestions': autocomplete_suggestions,
            'query_result': query_result_objs})
    

def sort_results(request):
    sort_by = request.POST.get('sort_by')
    keyword = request.POST.get('keyword')
    
    # Get the search results based on the keyword
    conditions = "short_description LIKE ?"
    query_values = tuple(f'%{keyword}%' for _ in range(1))
    query_result_objs = perform_search(query_values, conditions)

    # Apply sorting based on the selected sort_by option
    if sort_by == 'alphabetical':
        query_result_objs = sorted(query_result_objs, key=lambda x: x.headlines)
    elif sort_by == 'frequently_accessed':
        query_result_objs = sorted(query_result_objs, key=lambda x: x.access_count, reverse=True)
    elif sort_by == 'payment':
        query_result_objs = sorted(query_result_objs, key=lambda x: x.payment_amount, reverse=True)

    return render(request, 'search.html', {
        'total_results': len(query_result_objs),
        'query_result': query_result_objs})