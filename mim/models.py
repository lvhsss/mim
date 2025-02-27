from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import os

class MIM(models.Model):
    meme_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='memes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    avatar = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}"

    def delete(self, *args, **kwargs):
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)

class LastSubmission(models.Model):
    timestamp = models.DateTimeField(auto_now=True)

class Vote(models.Model):
    meme = models.ForeignKey(MIM, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes')
    is_like = models.BooleanField()

    class Meta:
        unique_together = ('meme', 'user')

class Comment(models.Model):
    meme = models.ForeignKey(MIM, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    admin_note = models.TextField(blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Comment by {self.user.username} on meme {self.meme.meme_id}"