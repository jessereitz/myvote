from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User

class Poll(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete='CASCADE', related_name='polls')



    def __str__(self):
        return self.name

class Option(models.Model):
    option_text = models.CharField(max_length=100)
    poll = models.ForeignKey(Poll, on_delete='CASCADE', related_name='options')

    def __str__(self):
        return self.option_text

class Vote(models.Model):
    option = models.ForeignKey(Option, on_delete='CASCADE', related_name='votes')
    owner = models.ForeignKey(User, on_delete='CASCADE', related_name='+')
    poll = models.ForeignKey(Poll, on_delete='CASCADE', related_name='+')
