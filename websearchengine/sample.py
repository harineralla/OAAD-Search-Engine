import os
import re
import pandas as pd
from django.shortcuts import render
from django.views import View
from adminapp.models import QueryResult
from django.http import JsonResponse
from django.db.models import Q


def is_valid_url(url):
    # Check if the URL matches the specified pattern
    pattern = r'^((http://|https://)?(www\.)?[a-zA-Z0-9]+\.)(edu|com|org|net|gov)$'
    return bool(re.match(pattern, url))


def index(request):
    return render(request, "index.html")


def search_results(keywords, search_type):
    csv_path = os.path.join(os.path.dirname(__file__), 'news_summary1.csv')
    dataframe = pd.read_csv(csv_path, encoding='unicode_escape', header='infer', usecols=[
                            'headlines', 'url', 'short_description'])

    if search_type == 'AND':
        values = keywords.split(" ")
        q_objects = Q()
        for value in values:
            q_objects &= Q(short_description__icontains=value)
    elif search_type == 'OR':
        values = keywords.split(" ")
        q_objects = Q()
        for value in values:
            q_objects |= Q(short_description__icontains=value)
    elif search_type == "NOT":
        values = keywords.split(" ")
        q_objects = ~Q()
        for value in values:
            q_objects &= ~Q(short_description__icontains=value)
    else:
        values = keywords.split(" ")
        q_objects = Q()
        for value in values:
            q_objects &= Q(short_description__icontains=value)

    query_result_objs = QueryResult.objects.filter(q_objects).order_by('headlines')

    valid_query_result = []
    urls_seen = set()
    for row in query_result_objs:
        if row.url not in urls_seen and is_valid_url(row.url):
            valid_query_result.append(row)
            urls_seen.add(row.url)

    return valid_query_result


class SearchView(View):
    template_name = 'search.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        keywords = request.POST.get('searchInput')
        search_type = request.POST.get('search_type')

        # Clear the database before adding new search results
        QueryResult.objects.all().delete()

        valid_query_result = search_results(keywords, search_type)

        query_result_objs = [
            QueryResult(
                headlines=row.headlines,
                short_description=row.short_description,
                url=row.url
            )
            for row in valid_query_result
        ]  # Create QueryResult objects for each valid record

        # Save all QueryResult objects in a single database query
        QueryResult.objects.bulk_create(query_result_objs)

        query_result_objs = QueryResult.objects.all()

        # Retrieve the values from QueryResult objects
        query_result_values = list(query_result_objs.values(
            'headlines', 'url', 'short_description'))

        # Convert the list of dictionaries to a DataFrame
        query_results = pd.DataFrame(query_result_values)[1:]

        return render(request, self.template_name, {
            'total_results': len(query_result_objs),
            'query_result': query_results})

    def sort_query_results(self, request):
        keywords = request.POST.get('searchInput')
        search_type = request.POST.get('search_type')
        sort_by = request.POST.get('sort_by')

        valid_query_result = search_results(keywords, search_type)

        if sort_by == 'alphabetical':
            valid_query_result = sorted(
                valid_query_result, key=lambda x: x.headlines)
        else:
            # Default sorting (no specific order)
            pass

        query_result_values = list(valid_query_result.values(
            'headlines', 'url', 'short_description'))

        # Convert the list of dictionaries to a DataFrame
        query_results = pd.DataFrame(query_result_values)[1:]

        return JsonResponse({
            'total_results': len(valid_query_result),
            'query_result': query_results.to_dict('records')
        })
