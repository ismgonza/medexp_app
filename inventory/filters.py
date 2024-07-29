from django.db.models import Q
from .models import InventoryItem

def filter_inventory_items(queryset, search_query=None, show_inactive=False):
    if not show_inactive:
        queryset = queryset.filter(active=True)

    if search_query:
        queryset = queryset.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    return queryset