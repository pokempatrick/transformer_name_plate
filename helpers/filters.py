from rest_framework import filters


class RootFilter(filters.SearchFilter):

    def get_search_fields(self, view, request):
        return ['added_by__first_name', 'added_by__last_name']
