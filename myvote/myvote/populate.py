from django.contrib.auth.models import User
from .models import Poll, Option, Vote

def populate_users_with_polls(user_count=10, poll_count=15):
    for i in range(0, user_count):
        USERNAME = "test_user_{0}".format(i)
        user = User.objects.create_user(username=USERNAME, password="password12", email=USERNAME + "@test.com")
        print("User " + user.username + " created.")
        for j in range(0, poll_count):
            POLL_NAME = USERNAME + "'s poll #" + str(j)
            poll = Poll(name=POLL_NAME, owner=user)
            poll.save()
            option1 = Option(option_text="yes", poll=poll)
            option1.save()
            option2 = Option(option_text="no", poll=poll)
            option2.save()

            print("Poll " + POLL_NAME + " created.")
