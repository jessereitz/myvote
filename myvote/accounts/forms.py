from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):

    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(max_length=72, widget=forms.PasswordInput())
    new_password = forms.CharField(max_length=72, widget=forms.PasswordInput())
    new_password2 = forms.CharField(max_length=72, widget=forms.PasswordInput())

    def __init__(self, user=None, data=None):
        super().__init__(data=data)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password = cleaned_data.get('new_password')
        new_password2 = cleaned_data.get('new_password2')

        if not self.user.check_password(old_password):
            raise forms.ValidationError("Incorrect old password.")

        if not new_password == new_password2:
            raise forms.ValidationError("New passwords must match.")

        return cleaned_data
