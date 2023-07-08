import os
import pandas as pd
import sqlite3
from django.shortcuts import render
from django.views import View
from adminapp.models import QueryResult
from django.http import JsonResponse
from django.db.models import Q
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
        sort_by = request.POST.get('sort_by')  # New - Get the sort_by parameter

        csv_path = os.path.join(os.path.dirname(__file__), 'news_summary1.csv')
        dataframe = pd.read_csv(csv_path, encoding='unicode_escape', header='infer', usecols=[
                                'headlines', 'url', 'short_description'])
        # dataframe = pd.read_csv('news_summary1.csv', encoding='unicode_escape', header='infer', usecols=['headlines', 'url', 'short_description'])

        conn = sqlite3.connect(':memory:')
        dataframe.to_sql('data_table', conn, index=False)

        # breakpoint()
        if search_type == 'AND':
            values = keyword.split()
            conditions = " AND ".join(
                ["short_description LIKE ?"] * len(values))
            query = f"SELECT * FROM data_table WHERE {conditions}"
            query_values = tuple(f'%{value}%' for value in values)
        elif search_type == 'OR':
            values = keyword.split()
            conditions = " OR ".join(
                ["short_description LIKE ?"] * len(values))
            query = f"SELECT * FROM data_table WHERE {conditions}"
            query_values = tuple(f'%{value}%' for value in values)
        elif search_type == "NOT":
            values = keyword.split()
            conditions = " NOT ".join(
                ["short_description LIKE ?"] * len(values))
            query = f"SELECT * FROM data_table WHERE {conditions}"
            query_values = tuple(f'%{value}%' for value in values)
        else:
            values = keyword.split()
            conditions = "".join(["short_description LIKE ?"] * len(values))
            query = f"SELECT * FROM data_table WHERE {conditions}"
            query_values = tuple(f'%{value}%' for value in values)

        query_result = pd.read_sql_query(query, conn, params=query_values)

        # Convert the DataFrame to a list of dictionaries
        query_result_dict = query_result.to_dict('records')
        query_result_objs = [
            QueryResult(
                headings=row['headlines'],
                short_description=row['short_description'],
                url=row['url']
            )
            for row in query_result_dict
        ]  # Create QueryResult objects for each record

        # Save all QueryResult objects in a single database query
        QueryResult.objects.bulk_create(query_result_objs)

        # Retrieve autocomplete suggestions from the database based on the keyword
        suggestions = QueryResult.objects.filter(
            Q(headings__icontains=keyword) | Q(
                short_description__icontains=keyword)
        ).values_list('headings', flat=True)[:5]  # Change the field names as per your model

        autocomplete_suggestions = list(suggestions)

        # Apply sorting based on the selected sort_by option
        if sort_by == 'alphabetical':
            query_result_objs = QueryResult.objects.order_by('headings')
        elif sort_by == 'frequently_accessed':
            query_result_objs = QueryResult.objects.order_by('-access_count')
        elif sort_by == 'payment':
            query_result_objs = QueryResult.objects.order_by('-payment_amount')
        else:
            # Default sorting (no specific order)
            query_result_objs = QueryResult.objects.all()

        conn.close()

        return render(request, self.template_name, {'query_result': query_result,
                                                    'total_results': len(query_result_objs),
                                                    'autocomplete_suggestions': autocomplete_suggestions,
                                                    'query_result': query_result_objs})

    # def autocomplete(self, request):
    #     keyword = request.GET.get('keyword')

    #     # Retrieve autocomplete suggestions from the database based on the keyword
    #     suggestions = QueryResult.objects.filter(
    #         Q(headings__icontains=keyword) | Q(
    #             short_description__icontains=keyword)
    #     ).values_list('headings', flat=True)[:5]  # Change the field names as per your model

    #     autocomplete_suggestions = list(suggestions)

    #     return render(request, 'search.html', {'autocomplete_suggestions': autocomplete_suggestions})
