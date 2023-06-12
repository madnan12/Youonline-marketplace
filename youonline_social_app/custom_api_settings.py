from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data, details=None, playlist=None):
        return Response({
            'links': {
               'next': self.get_next_link(),
               'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'per_page_result': self.page_size,
            'results': data,
            'details': details,
            'playlist': playlist,
        })


class NewsFeedPagination(PageNumberPagination):
    def get_paginated_response(self, data, details=None, playlist=None):
        # Code to get 10 results on first page.
        if self.get_previous_link():
            per_page_results = self.page_size
        else:
            per_page_results = 10
        return Response({
            'links': {
               'next': self.get_next_link(),
               'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'per_page_result': per_page_results,
            'results': data,
            'details': details,
            'playlist': playlist,
        })