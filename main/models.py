from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_imgs/', default='default-profile-img.png')
    profilecover = models.ImageField(upload_to='profile_covers/', default='default-profile-cover.png')
    location = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.user.username
    
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4)
    user = models.CharField(max_length=50)
    image = models.ImageField(upload_to='post_imgs')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    num_of_likes = models.IntegerField(default = 0)

    def __str__(self):
        return self.user
    
class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=50)

    def __str__(self):
        return self.username

class FollowersCount(models.Model):
    follower = models.CharField(max_length=50)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user
    
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    action_type = models.CharField(max_length=50)  # e.g., "like" or "follow"
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)  # If the notification is related to a post
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.sender.username} {self.action_type} {self.recipient.username}"