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
    post_list = Post.objects.all().filter(group=group)
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
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new.html', {'form': form})
    form = PostForm()
    return render(request, 'new.html', {'form': form})
    

def profile(request, username):
    author = User.objects.get(username=username)
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 
        'profile.html', 
        {'page': page, 'paginator': paginator, 'author': author}
        )


def post_view(request, username, post_id):
        user = get_object_or_404(User, username=username)
        post = get_object_or_404(Post, author=user, id=post_id)
        return render(
            request,
            'post.html',
            { 'post': post, 'author': user }
            )


def post_edit(request, username, post_id):
        user = get_object_or_404(User, username=username)
        login_user = request.user
        post = get_object_or_404(Post, author=user, id=post_id)
        if login_user != user:
            return redirect('post', username=user, post_id=post_id)
        form = PostForm()
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('post', username=user, post_id=post_id)
            return render(request, 'new.html', {'form': form, 'post': post})
        form = PostForm(instance=post)
        return render(request, 'new.html', {'form': form, 'post': post})