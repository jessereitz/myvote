from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.contrib.auth.password_validation import (validate_password,
        MinimumLengthValidator, CommonPasswordValidator,
        NumericPasswordValidator,)

class SignUpForm(UserCreationForm):

    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(max_length=72, required=True, widget=forms.PasswordInput())
    new_password = forms.CharField(max_length=72, required=True, widget=forms.PasswordInput())
    new_password2 = forms.CharField(max_length=72, required=True, widget=forms.PasswordInput())

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

        if not new_password or not new_password == new_password2:
            raise forms.ValidationError("New passwords must match.")

        if not any(char.isdigit() for char in new_password):
            raise forms.ValidationError("New password must include at least one number.")

        validate_password(password=new_password, user=self.user)

        return cleaned_data

class ChangeEmailForm(forms.Form):
    password = forms.CharField(max_length=72, required=True, widget=forms.PasswordInput())
    new_email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    new_email2 = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())

    def __init__(self, user=None, data=None):
        super().__init__(data=data)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        new_email = cleaned_data.get('new_email')
        new_email2 = cleaned_data.get('new_email2')

        if not self.user.check_password(password):
            raise forms.ValidationError("Incorrect password.")

        if not new_email == new_email2:
            raise forms.ValidationError("New emails must match.")

        validate_email(new_email)

        return cleaned_data

class DeleteAccountForm(forms.Form):
    password = forms.CharField(max_length=72, required=True, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=72, required=True, widget=forms.PasswordInput())
