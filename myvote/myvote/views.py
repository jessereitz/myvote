from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Poll, Option, Vote
from .forms import PollCreationForm, PollDeletionForm

def index(request):
    """ Renders homepage/index view. """
    if request.user.is_authenticated:
        polls = Poll.objects.filter(owner=request.user)
        followed_users = request.user.followed.all()
    else:
        polls = None
    return render(request, 'myvote/index.html', {'polls': polls, 'followed_users': followed_users})


@login_required
def create_poll(request):
    if request.method == 'POST':
        form = PollCreationForm(request.POST)
        if form.is_valid():
            poll_name = form.cleaned_data['name']
            poll = Poll(name=poll_name, owner=request.user)
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
    poll = get_object_or_404(Poll, pk=poll_id)
    if poll.user_has_voted(request.user):
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
            return render(request, 'myvote/delete_poll.html', {'poll': poll, 'form': form})
    else:
        # if current user is NOT poll owner, redirect home
        messages.add_message(request, messages.ERROR, "You do not have permission to delete that poll")
        return redirect(reverse('home'))
