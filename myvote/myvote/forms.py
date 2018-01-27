from django import forms


class PollCreationForm(forms.Form):
    DESC_PLACEHOLDER = "optional description of your poll"
    name = forms.CharField(label="poll name", max_length=100)
    description = forms.CharField(label="description", required=False,
                                  widget=forms.Textarea(attrs=
                                    {'placeholder': DESC_PLACEHOLDER})
                                  )
    option1 = forms.CharField(label="option 1", max_length=100)
    option2 = forms.CharField(label="option 2", max_length=100)

class PollDeletionForm(forms.Form):
    pass
