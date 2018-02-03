from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from .models import Poll, Option, Vote
from .forms import PollCreationForm, PollDeletionForm

def index(request):
    """ Renders homepage/index view. """
    if request.user.is_authenticated:
        followed_users = request.user.followed.values_list('followed_id')
        followed_poll_list = Poll.objects.filter(owner_id__in=followed_users).order_by('-datetime')

        paginator = Paginator(followed_poll_list, 5)
        page = request.GET.get('page')
        followed_polls = paginator.get_page(page)
    else:
        followed_users = None
        followed_polls = None
    return render(request, 'myvote/index.html',
                  {'followed_polls': followed_polls})

def explore_polls(request):
    """
        Allows users to explore and find polls. As of now explore simply
        displays all polls in system, ordered by datetime added descending.
        Produces two values for use in template: 'page_title', and 'polls'.

        Template values:
            -  page_title = a String representing the title of the page.
            -  polls = a query_set of Poll objects, ordered by posted datetime
                       descending.
    """
    page_title = "Explore Polls"
    poll_list = Poll.objects.all().order_by('-datetime')
    paginator = Paginator(poll_list, 10)
    page = request.GET.get('page')
    polls = paginator.get_page(page)
    return render(request, 'myvote/recent_polls.html',
                  {'page_title': page_title, 'polls': polls})


def explore_recent_polls(request, user_id):
    """
        Allows users to view all recent polls from a given user. Produces two
        values for use in template: 'page_title', and 'polls'.

        Template values:
            -  page_title = a String representing the title of the page.
            -  polls = a query_set of Poll objects, ordered by posted datetime
                       descending.
    """
    view_user = User.objects.get(pk=user_id)
    page_title = view_user.username + "'s Recent Polls"
    poll_list = view_user.polls.order_by('-datetime')
    paginator = Paginator(poll_list, 10)
    page = request.GET.get('page')
    polls = paginator.get_page(page)
    return render(request, 'myvote/recent_polls.html',
                  {'page_title': page_title, 'polls': polls})

def search_all(request):
    search_val = request.GET.get('search_val')

    if search_val:
        user_search_results = User.objects.filter(username__icontains=search_val)[:3]
        poll_vector = SearchVector('name', weight='A') + SearchVector('description', weight='B')
        poll_query = SearchQuery(search_val)
        poll_search_results = Poll.objects.annotate(rank=SearchRank(poll_vector, poll_query)).filter(rank__gte=0.3).order_by('rank')[:3]
    else:
        user_search_results = None
        poll_search_results = None

    return render(request, 'myvote/search_all.html',
                  {'user_search_results': user_search_results,
                   'poll_search_results': poll_search_results,
                   'search_val': search_val,})

def search_users(request):
    search_val = request.GET.get('search_val')

    if search_val:
        user_search_results_list = User.objects.filter(username__icontains=search_val)
        paginator = Paginator(user_search_results_list, 10)
        page = request.GET.get('page')
        user_search_results = paginator.get_page(page)
    else:
        user_search_results = None

    return render(request, 'myvote/search_generic.html',
                  {'results': user_search_results,
                   'result_type': 'User',
                   'search_val': search_val,})

def search_polls(request):
    search_val = request.GET.get('search_val')

    if search_val:
        poll_vector = SearchVector('name', weight='A') + SearchVector('description', weight='B')
        poll_query = SearchQuery(search_val)
        poll_search_results_list = Poll.objects.annotate(rank=SearchRank(poll_vector, poll_query)).filter(rank__gte=0.3).order_by('rank')
        paginator = Paginator(poll_search_results_list, 10)
        page = request.GET.get('page')
        poll_search_results = paginator.get_page(page)
    else:
        poll_search_results = None

    return render(request, 'myvote/search_generic.html',
                  {'results': poll_search_results,
                   'result_type': 'Poll',
                   'search_val': search_val,})


@login_required
def create_poll(request):
    """
        If GET request, displays PollCreationForm. If POST, validates
        PollCreationForm and creates a poll based with given information.
    """
    if request.method == 'POST':
        options = [val for key, val in request.POST.items() if 'option' in key]
        form = PollCreationForm(request.POST, options=options)
        if form.is_valid():
            poll_name = form.cleaned_data['name']
            poll_description = form.cleaned_data['description']
            poll = Poll(name=poll_name,
                        description=poll_description,
                        owner=request.user)
            poll.save()

            options = [val for key, val in form.cleaned_data.items() if 'option' in key]
            for option in options:
                option = Option(option_text=option, poll=poll)
                option.save()
            # print('\n\n\n')
            # print(options)
            # print('\n\n\n')

            # option1_text = form.cleaned_data['option1']
            # option1 = Option(option_text=option1_text, poll=poll)
            # option1.save()

            # option2_text = form.cleaned_data['option2']
            # option2 = Option(option_text=option2_text, poll=poll)
            # option2.save()

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
    return render(request, 'myvote/view_poll.html',
                  {'poll': poll, 'user_has_voted': user_has_voted})

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


# HELPERS #
def get_recent_polls(user_id):
    """
        Helper function that gets recent polls
    """
