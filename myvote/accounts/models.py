from django.db import models
from django.contrib.auth.models import User

class FollowedUsers(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed")
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")

class UserBio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="bio")
    text = models.TextField()
