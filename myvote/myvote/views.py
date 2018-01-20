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
            print("\n\n\n\npoll id")
            print(poll.id)

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

    return render(request, 'myvote/view_poll.html', {'poll': poll})

def vote_poll(request, poll_id, option_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    option = poll.options.filter(pk=option_id)
    vote = Vote.objects.filter(owner=request.user, poll=poll)
    if option and vote:
        print("there's a vote and option!")
    elif option:
        print("there's no vote! But there is an option!")
    else:
        print("theres nothing....")

    return redirect(reverse('view poll', args=(poll.id,)))
    # if not get_object_or_404(Vote, owner=request.user):
    #     print("\n\n\n\nNo vote for this user")
    # option = get_object_or_404(Option, pk=option_id)
    # vote = Vote(option=option, owner=request.user)
    # vote.save()
