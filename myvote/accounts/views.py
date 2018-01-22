from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import SignUpForm, ChangePasswordForm, ChangeEmailForm, DeleteAccountForm
from .models import FollowedUsers

# TODO: Recent polls (votes?) on homepage
# TODO: Viewable profile pages
# TODO: Profile search? Maybe not though...
# TODO: Share poll buttons
# TODO: Email notifications (follows, and votes)
# TODO: Make email notifications subscribable (add to account_overview)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "You're all signed up! Welcome to MyVote!")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def follow_user(request, user_id):
    if request.method == 'POST':
        next_url = request.POST.get('next') or 'home'
        if request.user.id == user_id:
            messages.error(request, "You cannot follow yourself.")
            return redirect(next_url)
        try:
            followed_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            messages.error(request, "This user does not exist.")
            return redirect('home')
        try:
            relationship = FollowedUsers.objects.get(follower=request.user, followed=followed_user)
        except FollowedUsers.DoesNotExist:
            relationship = FollowedUsers(follower=request.user, followed=followed_user)
            relationship.save()
        return redirect(next_url)
    return redirect('home')

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

            return redirect('home')
    return render(request, 'accounts/delete_account.html', {'form': form})
