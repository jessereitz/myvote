from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import SignUpForm, ChangePasswordForm, ChangeEmailForm, DeleteAccountForm
from .models import FollowedUsers

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
        next_url = request.POST.get('next_url') or 'home'
        if request.user.id == user_id:
            messages.warning(request, "You cannot follow yourself.")
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
def unfollow_user(request, user_id):
    if request.method == 'POST':
        next_url = request.POST.get('next_url') or 'home'
        if request.user.id == user_id:
            messages.warning(request, "You cannot unfollow yourself.")
            return redirect(next_url)
        try:
            relationship = FollowedUsers.objects.get(follower=request.user, followed_id=user_id)
            relationship.delete()
        except Exception as e:
            # TODO: implement logging
            print(e)
        return redirect(next_url)


@login_required
def account_settings(request):
    """
        Display the settings page.
    """
    if request.user.is_authenticated:
        return render(request, 'accounts/account_settings.html')

def account_view_profile(request, user_id):
    """
        Display the profile page for a user. Includes username, recent polls.
    """
    if not user_id:
        return redirect('home')
    else:
        if request.user.is_authenticated:
            if request.user.id == user_id:
                print('\n\n\nEYYYY')
                view_user = request.user
                followed = "Self"
            else:
                try:
                    relationship = request.user.followed.filter(followed_id=user_id).first()
                    view_user = relationship.followed
                    followed = True
                except Exception as e:
                    view_user = get_object_or_404(User, pk=user_id)
                    followed = False
        else:
            view_user = get_object_or_404(User, pk=user_id)
            followed = None

        print(view_user)
        print(followed)
        return render(request, 'accounts/view_profile.html', {'view_user': view_user, 'followed': followed})
    return redirect('home')

@login_required
def change_password(request):
    if request.method == 'GET':
        # This has to manually be set to None because of the way the form
        # clean method works.
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
        # This has to manually be set to None because of the way the form
        # clean method works.
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
        # This has to manually be set to None because of the way the form
        # clean method works.
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
