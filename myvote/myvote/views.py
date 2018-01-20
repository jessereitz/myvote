from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Poll, Option, Vote
from .forms import PollCreationForm

def index(request):
    """ Renders homepage/index view. """
    return render(request, 'myvote/index.html')


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
    # if not get_object_or_404(Vote, owner=request.user):
    #     print("\n\n\n\nNo vote for this user")
    # option = get_object_or_404(Option, pk=option_id)
    # vote = Vote(option=option, owner=request.user)
    # vote.save()
