from django import forms


class PollCreationForm(forms.Form):
    name = forms.CharField(label="poll name", max_length=100)
    option1 = forms.CharField(label="option 1", max_length=100)
    option2 = forms.CharField(label="option 2", max_length=100)
