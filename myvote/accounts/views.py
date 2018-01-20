from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required

from .forms import SignUpForm


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
    # TODO:
    #   1 - Display link to change password
    #   2 - Display link to change email
    #   3 - Display link to delete account
    if request.user.is_authenticated:
        return render(request, 'accounts/account_overview.html')

@login_required
def change_password(request):
    pass

@login_required
def change_email(request):
    pass

@login_required
def delete_account(request):
    pass
