from django import forms

class EmailForm(forms.Form):
    email = forms.EmailField()
    subject = forms.CharField(max_length=100)
    attach = forms.FileField(widget=forms.ClearableFileInput(), required = False)
    message = forms.CharField(widget = forms.Textarea)


class EmailFormNoAddress(forms.Form):
    subject = forms.CharField(max_length=100)
    attach = forms.FileField(widget=forms.ClearableFileInput(), required = False)
    message = forms.CharField(widget = forms.Textarea)
