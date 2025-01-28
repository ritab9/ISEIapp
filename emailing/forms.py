from django import forms


#Used with teacher Cert Emailing that should be totally redone
class EmailForm(forms.Form):
    email = forms.EmailField()
    subject = forms.CharField(max_length=100)
    attach = forms.FileField(widget=forms.ClearableFileInput(), required = False)
    message = forms.CharField(widget = forms.Textarea)


class EmailFormNoAddress(forms.Form):
    subject = forms.CharField(max_length=100)
    attach = forms.FileField(widget=forms.ClearableFileInput(), required = False)
    message = forms.CharField(widget = forms.Textarea)
