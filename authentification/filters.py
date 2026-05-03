from rest_framework import filters

from helpers.constant import ROLE_MANAGER

class UserFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        return ['id', 'first_name', 'last_name',
                     'role_name', 'added_by', 'email', 'username']
    
    def filter_queryset(self, request, queryset, view):
        user = request.user
        if request.user.role_name in ROLE_MANAGER:
            queryset = queryset.exclude(role_name="ROLE_ADMIN"
                ).filter(is_active=True)
        if request.user.role_name in ["ROLE_TECHNICIEN", "ROLE_ANONYME"]:
            queryset = queryset.filter(id=user.id, is_active=True)
        
        return super().filter_queryset(request, queryset, view)
        