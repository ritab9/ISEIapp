from django import forms
from .models import AnnualVisit

class AnnualVisitForm(forms.ModelForm):
    class Meta:
        model = AnnualVisit
        fields = ["visit_date", "representative", "notes"]
        widgets = {
            "visit_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "representative": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 1}),
        }
