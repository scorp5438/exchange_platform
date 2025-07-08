from collections import OrderedDict
from math import ceil

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class InfiniteScrollPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    limit_query_param = 'limit'
    offset_query_param = 'offset'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('count_page', ceil(self.page.paginator.count / self.page_size)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
