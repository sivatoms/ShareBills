from django.contrib import admin
from .models import Post
# Register your models here.

class postAdmin(admin.ModelAdmin):
    list_display = ['post_title', 'post_description','post_date']
    class Meta:
        model = Post            

admin.site.register(Post, postAdmin)
