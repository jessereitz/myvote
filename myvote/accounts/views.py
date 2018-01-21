from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from .forms import SignUpForm, ChangePasswordForm, ChangeEmailForm, DeleteAccountForm


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
    if request.method == 'GET':
        request.POST = None
    form = ChangePasswordForm(data=request.POST, user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            messages.add_message(request, messages.SUCCESS, "Password successfully changed. Please login with your new password.")
            return redirect('account:overview')

    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def change_email(request):
    if request.method == 'GET':
        request.POST = None

    form = ChangeEmailForm(data=request.POST, user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            request.user.email = form.cleaned_data['new_email']
            request.user.save()
            messages.add_message(request, messages.SUCCESS, 'Email successfully updated')
            return redirect('account:overview')
    return render(request, 'accounts/change_email.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == 'GET':
        request.POST = None

    form = DeleteAccountForm(data=request.POST, user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            try:
                user = User.objects.get(pk=request.user.id)
                user.delete()
                messages.success(request, 'Your profile has been deleted.')
            except User.DoesNotExist:
                messages.error(request, "This user does not exist.")
            except Exception:
                messages.error(request, "Something went wrong. Please try again.")
            else:
                return redirect('home')
    return render(request, 'accounts/delete_account.html', {'form': form})
