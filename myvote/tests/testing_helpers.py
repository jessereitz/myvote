from django.contrib.auth.models import User
from myvote.models import Poll, Option, Vote

# DEFAULT CONSTANTS
USERNAME = 'testuser'
PASSWORD = 'testpassword12'

def create_test_user(username=None, password=None):
    """
        Creates a test user in the db. Uses given username and password or
        default username and password constants.
    """
    if username:
        username = username
    else:
        username = USERNAME
    if password:
        password = password
    else:
        password = PASSWORD
    return User.objects.create_user(username=username, password=password)

def create_polls(user, start_num=0, amount=10):
    """
        Populates db with a number of test polls with 2 options. If no amount
        given, defaults to 10. MUST have 'user' supplied.
    """
    POLL_NAME = "test_poll_"
    OPTION_1 = 'option1'
    OPTION_2 = 'option2'

    if not user:
        raise Exception("User not provided.")

    for i in range(start_num, amount + start_num):
        new_name = POLL_NAME + str(i)
        p = Poll(owner=user, name=new_name)
        p.save()

        option_1 = Option(option_text=OPTION_1, poll=p)
        option_1.save()

        option_2 = Option(option_text=OPTION_2, poll=p)
        option_2.save()
