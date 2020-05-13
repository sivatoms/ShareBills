from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib.auth.views import LoginView, LogoutView

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .forms import Post_Form, Post_Edit
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from django.views.generic import TemplateView
# Create your views here.
'''
def home(request):
    return HttpResponse("Created first page")
'''
def home(request):
    return render(request, 'base.html')

def save_post_form(request):
    if request.method == 'POST':
        form = Post_Form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post_list')
    else:
        form = Post_Form()
    return render(request, 'posts_t/postform.html', {'form':form})

def posts_list(request):
    queryset_list = Post.objects.all()
    
    query = request.GET.get('q')
    if query:
        queryset_list = queryset_list.filter(
            Q(post_title__icontains=query)|
            Q(post_description__icontains=query)
        ).distinct()
    paginator = Paginator(queryset_list, 4)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)
    
    context_data = {
        'object_list':queryset,
        'title':'List',
        'page_request_var':page_request_var
    }

    return render(request, 'posts_t/posts_list.html',context_data)#{'posts':posts})


def post_detail(request, id):
    post = Post.objects.get(id=id)
    return render(request, 'posts_t/post_details.html',{'post':post})

def edit_post(request,id):
    post = Post.objects.get(id=id)    
    if request.method == 'POST':
        form = Post_Edit(request.POST, instance=post)       
        if form.is_valid():
            form.save()
            return redirect('post_list')
    else:
        form = Post_Edit(instance=post)    
        return render(request, 'posts_t/post_edit.html', {'form':form})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form':form})