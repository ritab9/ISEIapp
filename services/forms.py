from django import forms
from .models import *

class TestOrderForm(forms.ModelForm):
    class Meta:
        model = TestOrder
        fields = ['testing_dates', 'order_date', 'no_students_testing', 'sub_total', 'shipping', 'total']
        widgets = {
            'order_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'no_students_testing': forms.NumberInput(attrs={'style': 'width:100px;'}),
        }


ReusableTestBookletFormSet = forms.inlineformset_factory(
    TestOrder,
    ReusableTestBookletOrdered,
    fields=['level', 'count'],
    widgets={'count': forms.NumberInput(attrs={'style': 'width:100px;'})},
    extra=5,
)

AnswerSheetFormSet = forms.inlineformset_factory(
    TestOrder,
    AnswerSheetOrdered,
    fields=['level', 'count'],
    widgets={'count': forms.NumberInput(attrs={'style': 'width:100px;'})},
    extra=5,
)

DirectionBookletFormSet = forms.inlineformset_factory(
    TestOrder,
    DirectionBookletOrdered,
    fields=['level', 'count'],
    widgets={'count': forms.NumberInput(attrs={'style': 'width:100px;'})},
    extra=2,
)
