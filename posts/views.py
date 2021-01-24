from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

PER_PAGE = settings.PER_PAGE


def page_not_found(request, exception=None):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


def index(request):
    post_list = Post.objects.select_related('group')
    paginator = Paginator(post_list, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'posts': post_list, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'page': page,
        'paginator': paginator
    }
    return render(request, 'group.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = (
        request.user.is_authenticated and
        request.user != user and
        Follow.objects.filter(user=request.user,
                              author=user).exists()
    )
    context = {
        'author': user,
        'page': page,
        'paginator': paginator,
        'following': following,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    following = (
        request.user.is_authenticated and
        request.user != user and
        Follow.objects.filter(user=request.user,
                              author=user).exists()
    )
    context = {
        'author': post.author,
        'post': post,
        'comments': comments,
        'form': form,
        'following': following,
    }
    return render(request, 'post.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'post_edit.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    form.save()
    return redirect('index')


@login_required
def post_edit(request, username, post_id):
    if username != request.user.username:
        return redirect('new_post')
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)
    return render(
        request, 'post_edit.html',
        {'form': form, 'post': post}
    )


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comments = form.save(commit=False)
        comments.author = request.user
        comments.post = post
        comments.save()
        return redirect('post', username, post_id)
    return render(
        request, 'includes/comments.html', {
            'form': form, 'post': post})


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user)
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow, user=request.user,
        author__username=username).delete()
    return redirect('profile', username)
