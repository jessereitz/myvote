from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from .models import Poll, Option, Vote
from .forms import PollCreationForm, PollDeletionForm

def index(request):
    """ Renders homepage/index view. """
    # TODO: AJAX load more polls at end of page?
    if request.user.is_authenticated:
        followed_users = request.user.followed.values_list('followed_id')
        followed_poll_list = Poll.objects.filter(owner_id__in=followed_users).order_by('-datetime')

        paginator = Paginator(followed_poll_list, 5)
        page = request.GET.get('page')
        followed_polls = paginator.get_page(page)
    else:
        followed_users = None
        followed_polls = None
    return render(request, 'myvote/index.html', {'followed_polls': followed_polls})


@login_required
def view_recent_polls(request):
    page_title = "Recent Polls in Your Network"
    followed_users = request.user.followed.values_list('followed_id')
    poll_list = Poll.objects.filter(owner_id__in=followed_users).order_by('-datetime')

    paginator = Paginator(poll_list, 10)
    page = request.GET.get('page')
    polls = paginator.get_page(page)
    return render(request, 'myvote/recent_polls.html', {'page_title': page_title,'polls': polls})


def explore_polls(request):
    """
        Allows users to explore and find polls.
        "/explore"  -defaults to recent
        "/explore/user_id" - recent polls from user

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
    page_title = "Explore Polls"
    poll_list = Poll.objects.all()
    paginator = Paginator(poll_list, 10)
    page = request.GET.get('page')
    polls = paginator.get_page(page)
    return render(request, 'myvote/recent_polls.html', {'page_title': page_title, 'polls': polls})

@login_required
def create_poll(request):
    if request.method == 'POST':
        form = PollCreationForm(request.POST)
        if form.is_valid():
            poll_name = form.cleaned_data['name']
            poll_description = form.cleaned_data['description']
            poll = Poll(name=poll_name,
                        description=poll_description,
                        owner=request.user)
            poll.save()

            option1_text = form.cleaned_data['option1']
            option1 = Option(option_text=option1_text, poll=poll)
            option1.save()

            option2_text = form.cleaned_data['option2']
            option2 = Option(option_text=option2_text, poll=poll)
            option2.save()

            messages.success(request, 'Poll successfully created.')
            return redirect(reverse('view poll', args=(poll.id,)))
    else:
        form = PollCreationForm()

    return render(request, 'myvote/create_poll.html', {'form': form})


def view_poll(request, poll_id):
    # TODO: implement F() to protect against race conditions
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user.is_anonymous or poll.user_has_voted(request.user):
        user_has_voted = True
    else:
        user_has_voted = False
    return render(request, 'myvote/view_poll.html', {'poll': poll, 'user_has_voted': user_has_voted})

@login_required
def vote_poll(request, poll_id, option_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if poll.user_has_voted(request.user):
        messages.add_message(request, messages.ERROR, "You've already voted on this poll!")
    else:
        try:
            option = poll.options.get(pk=option_id)
        except Exception:
            messages.add_message(request, messages.ERROR, "No such option exists.")
        else:
            vote = Vote(option=option, owner=request.user, poll=poll)
            vote.save()
            messages.add_message(request, messages.SUCCESS, "Vote recorded successfully!")

    return redirect(reverse('view poll', args=(poll.id,)))

@login_required
def delete_poll(request, poll_id):
    """
        If current user is logged in and owns poll, deletes poll with given poll_id.
    """
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user == poll.owner:
        if request.method == 'POST':
            # if current user is poll owner and has submitted post request, delete poll
            deleted = poll.delete()
            messages.add_message(request, messages.SUCCESS, "Poll successfully deleted")
            return redirect(reverse('home'))
        else:
            # if current user is poll owner and submits get request, display delete form
            form = PollDeletionForm()
            cancel_url = request.GET.get('cancel')
            return render(request,
                          'myvote/delete_poll.html',
                          {'poll': poll,
                          'form': form,
                          'cancel_url': cancel_url })
    else:
        # if current user is NOT poll owner, redirect home
        messages.add_message(request, messages.ERROR, "You do not have permission to delete that poll")
        return redirect(reverse('home'))
