from django.contrib import admin
from django.urls import path, include
from .views import (
       home, 
       save_post_form, 
       posts_list, 
       edit_post,
       post_detail,
       signup
)
urlpatterns = [
    #path('', home, name='home'),
    path('save_form', save_post_form, name='post_form'),
    path('post_detail/<int:id>', post_detail, name='post_detail'),
    path('post_edit/<int:id>', edit_post, name='post_edit'),
    path('signup/', signup, name='signup'),
    path('', include('django.contrib.auth.urls')),
    path('list/', posts_list, name='post_list'),
]