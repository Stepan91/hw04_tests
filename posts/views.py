from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import CreateView
from .models import Post, Group, User
from .forms import PostForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.filter(group=group)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'page': page, 'paginator': paginator, 'group': group}
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form})
    

def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.filter(author=author)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 
        'profile.html', 
        {'page': page, 'paginator': paginator, 'author': author}
        )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author=User.objects.get(username=username), id=post_id)
    return render(
        request,
        'post.html',
        { 'post': post, 'author': post.author }
        )


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author=User.objects.get(username=username), id=post_id)
    if request.user != post.author:
        return redirect('post', username=post.author, post_id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post = form.save()
        return redirect('post', username=request.user.username, post_id=post_id)
    edit_flag = True
    group = get_object_or_404(Group)
    return render(
        request, 
        'new.html', 
        {'form': form, 'post': post, 'edit_flag': edit_flag,}
        )