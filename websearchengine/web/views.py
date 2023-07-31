import os
import re
import json
from django.http import JsonResponse
import pandas as pd
from django.shortcuts import render
from django.views import View
from adminapp.models import QueryResult
from django.core.paginator import Paginator
from django.conf import settings

# Read the CSV file only once during the initialization of the view
csv_path = os.path.join(os.path.dirname(__file__), 'news_summary1.csv')
dataframe = pd.read_csv(csv_path, encoding='unicode_escape', header='infer', usecols=[
                        'headlines', 'url', 'short_description'])
headlines_list = dataframe['headlines'].tolist()


def is_valid_url(url):
    # Check if the URL matches the specified pattern
    pattern = r'^((http://|https://)?(www\.)?[a-zA-Z0-9]+\.)(edu|com|org|net|gov|in|html)$'
    return bool(re.match(pattern, url))


class SearchView(View):
    template_name = 'search.html'
    items_per_page = 10
    template_name = 'search.html'
    FILTER_SYMBOLS = set("!@#$%^&*()_+-=[]{};:'\"<>,.?/\\|")

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        keywords = request.POST.get('searchInput')
        search_type = request.POST.get('search_type')
        is_autocomplete = request.GET.get('autocomplete')

        keywords = self.filter_symbols(keywords)
        query_results = self.perform_search(dataframe, keywords, search_type)
        self.clear_and_save_results(query_results)

        # Explicitly call the render_results method to handle pagination.
        return self.render_results(request)

    def render_results(self, request):
        query_results = QueryResult.objects.all()

        paginator = Paginator(query_results, self.items_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, self.template_name, {
            'total_results': paginator.count,
            'query_result': page_obj,
            'paginator': paginator
        })

    def perform_search(self, dataframe, keywords, search_type):
        # The search logic remains the same as before
        values = keywords.split()
        conditions = r"\s+&\s+".join(values)  # For 'AND'
        or_conditions = r"\s+\|\s+".join(values)  # For 'OR'

        if search_type == 'AND':
            query_results = dataframe[dataframe['short_description'].str.contains(
                conditions, regex=True, case=False)]
        elif search_type == 'OR':
            query_results = dataframe[dataframe['short_description'].str.contains(
                or_conditions, regex=True, case=False)]
        elif search_type == "NOT":
            not_conditions = ~dataframe['short_description'].str.contains(
                or_conditions, regex=True, case=False)
            query_results = dataframe[not_conditions]
        else:
            query_results = dataframe[dataframe['short_description'].str.contains(
                conditions, regex=True, case=False)]

        return query_results

    def clear_and_save_results(self, query_results):
        QueryResult.objects.all().delete()

        query_result_dict = query_results.drop_duplicates(
            subset=['headlines']).to_dict('records')
        query_result_objs = [
            QueryResult(
                headlines=row['headlines'],
                short_description=row['short_description'],
                url=row['url']
            )
            for row in query_result_dict
        ]

        QueryResult.objects.bulk_create(query_result_objs)

    def filter_symbols(self, text):
        return ''.join(char for char in text if char not in self.FILTER_SYMBOLS)

    @staticmethod
    def sort_query_results(request):
        sort_by = request.POST.get("sort_by")

        if sort_by == 'alphabetical':
            query_results = QueryResult.objects.order_by('headlines')
        elif sort_by == 'access_frequency':
            query_results = QueryResult.objects.order_by('-access_frequency')
        elif sort_by == 'payment':
            query_results = QueryResult.objects.order_by('payment')
        else:
            query_results = QueryResult.objects.all()

        paginator = Paginator(query_results, SearchView.items_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'search.html', {
            'total_results': paginator.count,
            'query_result': page_obj,
            'paginator': paginator
        })


def index(request):
    headlines_json = json.dumps(headlines_list)
    return render(request, "index.html", {"headlines_json": headlines_json})


def get_headlines(request):
    file_path = os.path.join(settings.BASE_DIR, 'data', 'headlines.json')
    with open(file_path, 'r') as file:
        data = json.load(file)
    return JsonResponse(data, safe=False)
    # return JsonResponse({'message': 'This view is accessible.'})
