from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User

class Poll(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polls')

    def __str__(self):
        return self.name

    def user_has_voted(self, user):
        for option in self.options.all():
            found_user = option.votes.filter(owner=user)
            if found_user:
                return True
        return False

class Option(models.Model):
    option_text = models.CharField(max_length=100)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')

    def __str__(self):
        return self.option_text

class Vote(models.Model):
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='votes')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='+')
