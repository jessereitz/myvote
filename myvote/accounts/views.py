from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator


from .forms import (SignUpForm, ChangePasswordForm,
                    ChangeEmailForm, DeleteAccountForm,
                    BioForm)
from .models import FollowedUsers, UserBio

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

def view_profile(request, user_id):
    """
        Display the profile page for a user. Includes username, recent polls.
        MUST be passed a user_id (otherwise it redirects). If not redirected,
        this method produces a 'view_user', a 'followed' enumeration, and a
        list of view_user's recent polls, ordered by posted date descending.

        Return values:
            -  view_user = a User object. Can be the authenticated user.
            -  followed = an enumeration with 4 possible values:
                            - None (request.user is not authenticated)
                            - 'Self' (request.user is viewing own profile)
                            - True (request.user is already following view_user)
                            - False (request.user is NOT following view_user)
            -  poll_list = a query_set of Poll objects, ordered by posted date
                           descending.
    """
    if not user_id:
        return redirect('home')
    else:
        # Get view user and set followed
        if request.user.is_authenticated and request.user.id == user_id:
            view_user = request.user
            followed = "Self"
        elif request.user.is_authenticated:
            try:
                view_user = request.user.followed.get(followed_id=user_id).followed
                followed = True
            except Exception as e:
                view_user = get_object_or_404(User, pk=user_id)
                followed = False
        else:
            view_user = get_object_or_404(User, pk=user_id)
            followed = None

        poll_list = view_user.polls.order_by('-datetime')[:10]

        return render(request, 'accounts/view_profile.html',
                      {'view_user': view_user, 'followed': followed,
                       'poll_list': poll_list})

@login_required
def edit_bio(request):
    """
        Allows users to update their bio. User must be logged in. Automatically
        updates the current authenticated user.
    """
    if request.method == 'POST':
        form = BioForm(request.POST)
        if form.is_valid():
            bio_text = form.cleaned_data['bio_text']
            # Try to update the user's bio first. Otherwise create a new one
            try:
                request.user.bio.text = bio_text
                request.user.bio.save()
            except AttributeError:
                bio = UserBio(user=request.user, text=bio_text)
                bio.save()
            return redirect(reverse('account:view profile', args=(request.user.id,)))
    else:
        form = BioForm(initial={'bio_text':request.user.bio.text})
    return render(request, 'accounts/edit_bio.html', {'form': form})


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
