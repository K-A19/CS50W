from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField('self', null=True, blank=True, related_name='follows', symmetrical=False)
    following = models.ManyToManyField('self', null=True, blank=True, related_name='follower', symmetrical=False)


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE ,related_name='posts')
    content = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"Post by {self.owner} at {self.timestamp}"
    
    def serialize(self):
        return {
            "content" : self.content
        }

