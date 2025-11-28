import django_filters
from .models import Issue


class IssueFilter(django_filters.FilterSet):
    """
    Filter set for Issue model.
    """
    status = django_filters.MultipleChoiceFilter(
        choices=Issue.Status.choices
    )
    category = django_filters.CharFilter(field_name='category_id')
    urgency = django_filters.MultipleChoiceFilter(
        choices=Issue.Urgency.choices
    )
    area = django_filters.CharFilter(lookup_expr='icontains')
    search = django_filters.CharFilter(method='filter_search')
    created_after = django_filters.DateFilter(
        field_name='created_at', 
        lookup_expr='gte'
    )
    created_before = django_filters.DateFilter(
        field_name='created_at', 
        lookup_expr='lte'
    )

    class Meta:
        model = Issue
        fields = ['status', 'category', 'urgency', 'area']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(title__icontains=value) |
            models.Q(description__icontains=value)
        )
