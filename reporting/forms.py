from django import forms
from reporting.models import Student
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from users.models import Country, TNCounty


class UploadFileForm(forms.Form):
    file = forms.FileField()

all_countries = [(country.pk, str(country)) for country in Country.objects.all()]
all_counties = [(county.pk, str(county)) for county in TNCounty.objects.all()]


class StudentForm(forms.ModelForm):
    country = forms.ChoiceField(choices=all_countries)
    TN_county = forms.ChoiceField(choices=all_counties)

    class Meta:
        model = Student

        #exclude = ('annual_report', 'id', 'age_at_registration')
        fields=('name', 'gender', 'address', 'us_state', 'TN_county', 'country', 'birth_date','age', 'grade_level', 'boarding', 'baptized','parent_sda',
                'status', 'registration_date','withdraw_date', 'location')
        field_order = ( 'name', 'gender', 'address', 'us_state', 'TN_county', 'country', 'birth_date', 'age', 'grade_level', 'boarding', 'baptized',
                'parent_sda', 'status', 'registration_date', 'withdraw_date', 'location')

        widgets = {
            'name': forms.TextInput(attrs={'style': 'max-width: 300px;'}),
            'address': forms.TextInput(attrs={'style': 'max-width: 300px;'}),
            'us_state': forms.Select(attrs={'style': 'max-width: 100px;'}),
            'TN_county': forms.Select(attrs={'style': 'max-width: 100px;'}),
            'country': forms.Select(attrs={'style': 'max-width: 100px;'}),  # forms.Select for foreign key
            'birth_date': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
            'age': forms.NumberInput (attrs={'min': 1, 'max': 110, 'style': 'max-width: 30px;'}),
            'baptized': forms.Select(attrs={'style': 'max-width: 100px;'}),
            'parent_sda': forms.Select(attrs={'style': 'max-width: 100px;'}),
            'status': forms.Select(attrs={'style': 'max-width: 100px;'}),  # forms.Select for choices field
            'grade_level': forms.Select(attrs={'style': 'max-width: 50px;'}),
            'registration_date': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
            'withdraw_date': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
            'location': forms.Select(attrs={'style': 'max-width: 100px;'}),  # forms.Select for choices field
        }

    def clean(self):
        cleaned_data = super().clean()

        # Get the PK value from cleaned_data
        country_pk = cleaned_data.get('country')
        county_pk = cleaned_data.get('TN_county')

        try:
            # If country PK exists, get the object and replace it in cleaned_data
            if country_pk:
                country_obj = Country.objects.get(pk=country_pk)
                cleaned_data['country'] = country_obj  # Replace the PK value with the corresponding instance

                us_state = cleaned_data.get('us_state')
                if country_obj.code == 'US' and not us_state:
                    self.add_error('us_state', ValidationError("required for US address"))

                    # If TN_county PK exists, get the object and replace it in cleaned_data
            if county_pk:
                county_obj = TNCounty.objects.get(pk=county_pk)
                cleaned_data['TN_county'] = county_obj  # Replace the PK value with the corresponding instance


            if 'TN_county' in self.fields:
                us_state = cleaned_data.get('us_state')
                TN_county = cleaned_data.get('TN_county')
                if not TN_county:
                    cleaned_data['TN_county'] = None
                if us_state == 'TN' and not TN_county:
                    self.add_error('TN_county', ValidationError("required for TN students"))
                if us_state != 'TN' and TN_county:
                    self.add_error('TN_county', ValidationError("only for TN students"))

        except ObjectDoesNotExist:
            self.add_error(ObjectDoesNotExist)

        print(cleaned_data)
        return cleaned_data
