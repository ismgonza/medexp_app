import django_filters
from django.db.models import Q
from .models import Patient

class PatientFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_fields', label="Search")

    class Meta:
        model = Patient
        fields = ['search']

    def search_fields(self, queryset, name, value):
        if not value:
            return queryset

        # Split the search value into individual terms
        terms = value.split()

        # Create a base query
        query = Q()

        # Add each term to the query
        for term in terms:
            query |= (
                Q(id_number__icontains=term) |
                Q(first_name__icontains=term) |
                Q(last_name1__icontains=term) |
                Q(last_name2__icontains=term)
            )

        return queryset.filter(query)
        
class PatientSearchFilter(PatientFilter):
    class Meta(PatientFilter.Meta):
        pass

    def search_fields(self, queryset, name, value):
        # Limit to 10 results for the search functionality
        return super().search_fields(queryset, name, value)[:10]