from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class BasePagination(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response(
            {
                "page": self.page.number,
                "page_size": len(self.page.object_list),
                "total_page_count": self.page.paginator.num_pages,
                "total_results_count": self.page.paginator.count,
                "results": data,
            }
        )
