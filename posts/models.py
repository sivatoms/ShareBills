from django.db import models

# Create your models here.

class Post(models.Model):
    post_title = models.CharField(null=True, blank=True,max_length=200)
    post_description = models.TextField(null=True, blank=True)
    post_date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.post_title

    # order posts
    class Meta:
        ordering = ['-id']
    
