from .models import Post
from django import forms

class Post_Form(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'post_title',
            'post_description'
        )

class Post_Edit(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'post_title',
            'post_description'
        )