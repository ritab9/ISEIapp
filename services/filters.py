import django_filters
from .models import TestOrder, School

class TestOrderFilter(django_filters.FilterSet):
    testing_dates_after = django_filters.DateFilter(
        field_name="order_date", lookup_expr="gte", label="Order Date After"
    )
    testing_dates_before = django_filters.DateFilter(
        field_name="order_date", lookup_expr="lte", label="Order Date Before"
    )

    class Meta:
        model = TestOrder
        fields = {
            "school": ["exact"],
            "submitted": ["exact"],
            "finalized": ["exact"],
        }
