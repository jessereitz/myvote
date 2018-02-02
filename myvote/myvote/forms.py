from django import forms


class PollCreationForm(forms.Form):
    DESC_PLACEHOLDER = "optional description of your poll"
    name = forms.CharField(label="poll name", max_length=100)
    description = forms.CharField(label="description", required=False,
                                  widget=forms.Textarea(attrs=
                                    {'placeholder': DESC_PLACEHOLDER})
                                  )
    # option1 = forms.CharField(label="option 1", max_length=100,
    #                           widget=forms.TextInput(attrs={'class': 'optionInput'}))
    # option2 = forms.CharField(label="option 2", max_length=100,
    #                           widget=forms.TextInput(attrs={'class': 'optionInput'}))

    def __init__(self, *args, **kwargs):
        try:
            options = kwargs.pop('options')
        except:
            options = None

        super(PollCreationForm, self).__init__(*args, **kwargs)

        if options:
            for i, option in enumerate(options):
                i = i + 1
                self.fields['option%s' % i] = forms.CharField(label='option%s' % i,
                                                              max_length=100,
                                                              widget=forms.TextInput(attrs={'class': 'optionInput'}))
        else:
            self.fields['option1'] = forms.CharField(label="option 1", max_length=100,
                                      widget=forms.TextInput(attrs={'class': 'optionInput'}))
            self.fields['option2'] = forms.CharField(label="option 2", max_length=100,
                                      widget=forms.TextInput(attrs={'class': 'optionInput'}))


class PollDeletionForm(forms.Form):
    pass
