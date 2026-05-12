import django_filters
from django import forms
from .models import TestOrder, School

class TestOrderFilter(django_filters.FilterSet):
    school = django_filters.ModelChoiceFilter(
        queryset=School.objects.filter(test=False, active=True).exclude(abbreviation='SS'),
        label='School',
        empty_label='All Schools'
    )
    submitted = django_filters.ChoiceFilter(
        choices=[('', 'All'), ('true', 'Submitted'), ('false', 'Not Submitted')],
        label='Submitted',
        method='filter_submitted',
        empty_label=None
    )
    finalized = django_filters.ChoiceFilter(
        choices=[('', 'All'), ('true', 'Finalized'), ('false', 'Not Finalized')],
        label='Finalized',
        method='filter_finalized',
        empty_label=None,
        initial='false'
    )
    order_date_after = django_filters.DateFilter(
        field_name="order_date",
        lookup_expr="gte",
        label="Order Date From",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )
    order_date_before = django_filters.DateFilter(
        field_name="order_date",
        lookup_expr="lte",
        label="Order Date To",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )

    def filter_submitted(self, queryset, name, value):
        if value == 'true':
            return queryset.filter(submitted=True)
        elif value == 'false':
            return queryset.filter(submitted=False)
        return queryset

    def filter_finalized(self, queryset, name, value):
        if value == 'true':
            return queryset.filter(finalized=True)
        elif value == 'false':
            return queryset.filter(finalized=False)
        return queryset

    def __init__(self, data=None, *args, **kwargs):
        if not data:  # catches both None and empty QueryDict
            data = {'finalized': 'false'}
        else:
            data = data.copy()
        super().__init__(data, *args, **kwargs)

    class Meta:
        model = TestOrder
        fields = ['school', 'submitted', 'finalized', 'order_date_after', 'order_date_before']