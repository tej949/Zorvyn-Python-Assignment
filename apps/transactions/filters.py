"""Filters for Transactions app"""
from django_filters import rest_framework as filters
from apps.transactions.models import Transaction
from django.conf import settings
import django_filters


class TransactionFilter(filters.FilterSet):
    """Filter for transactions"""
    
    type = django_filters.ChoiceFilter(
        choices=Transaction.TYPE_CHOICES,
        field_name='type'
    )
    
    category = django_filters.ChoiceFilter(
        choices=[(cat, cat.title()) for cat in settings.FINANCE_CATEGORIES],
        field_name='category'
    )
    
    start_date = django_filters.DateFilter(
        field_name='date',
        lookup_expr='gte'
    )
    
    end_date = django_filters.DateFilter(
        field_name='date',
        lookup_expr='lte'
    )
    
    min_amount = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='gte'
    )
    
    max_amount = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='lte'
    )
    
    class Meta:
        model = Transaction
        fields = ['type', 'category', 'start_date', 'end_date', 'min_amount', 'max_amount']
