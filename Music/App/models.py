from django.db import models
from django.contrib.auth import get_user_model

class Playlist(models.Model):
    text=models.CharField(max_length=200)
    user=models.ForeignKey(get_user_model(),on_delete=models.CASCADE,null=True,related_name='playlists')
    selected=models.BooleanField(default=False)

class Song(models.Model):
    url=models.CharField(max_length=200)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=True, related_name='songs')
    title=models.CharField(max_length=200)