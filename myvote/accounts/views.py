from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from .forms import SignUpForm, ChangePasswordForm


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def account_overview(request):
    if request.user.is_authenticated:
        return render(request, 'accounts/account_overview.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            messages.add_message(request, messages.SUCCESS, "Password successfully changed. Please login with your new password.")
            return redirect('account:overview')
    else:
        form = ChangePasswordForm()
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def change_email(request):
    pass

@login_required
def delete_account(request):
    pass
