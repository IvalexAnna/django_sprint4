from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count

from . import const
from .models import Category, Post, Comment, User
from .forms import PostForm, EditProfileForm, CommentForm, DeletePostForm


User = get_user_model()


def get_posts():
    return Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


def get_categories():
    return Category.objects.filter(is_published=True)


def index(request):
    posts = get_posts().annotate(comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    num_pages = request.GET.get('page')
    page_obj = paginator.get_page(num_pages)
    return render(request, "blog/index.html", {"page_obj": page_obj})


def post_detail(request, pk):
    post = get_object_or_404(get_posts().annotate(comment_count=Count('comments')), pk=pk)
    comments = Comment.objects.filter(post_id=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', pk=pk)
    else:
        form = CommentForm()
    return render(request, "blog/detail.html", {"post": post, "form": form, "comments": comments})


def category_posts(request, category_slug):
    category = get_object_or_404(get_categories() , slug=category_slug)
    posts = category.posts.filter(pub_date__lte=timezone.now(),
                                  is_published=True).annotate(comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    num_pages = request.GET.get('page')
    page_obj = paginator.get_page(num_pages)
    return render(request, "blog/category.html",
                  {"page_obj": page_obj, "category": category})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if post.pub_date <= timezone.now():
                post.status = 'published'
            else:
                post.status = 'scheduled'
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile).annotate(comment_count=Count('comments')).order_by('-pub_date')
    is_owner = request.user == profile
    paginator = Paginator(posts, 10)
    num_pages = request.GET.get('page')
    page_obj = paginator.get_page(num_pages)

    return render(request, 'blog/profile.html',  {
        'profile': profile,
        'user': request.user,
        'page_obj': page_obj,
        'is_owner': is_owner,
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'blog/user.html', {'form': form})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post_id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', pk=post_id)
    else: 
        form = CommentForm()
    return render(request, 'blog/detail.html', {'post': post,'form': form, "comments": comments})

@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id, author=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk=post_id)
    else:
        form = CommentForm(instance=comment)
    comments = Comment.objects.filter(post_id=post_id)
    post = get_object_or_404(get_posts(), pk=post_id)
    return render(request, 'blog/detail.html', {'post': post, 'form': form, "comments": comments, 'comment': comment})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    comments = Comment.objects.filter(post_id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk=post_id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/detail.html', {'post': post, "form": form, "comments": comments})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    #form = PostForm(instance=post)
    comments = Comment.objects.filter(post_id=post_id)
    if request.method == 'POST':
        delete_form = DeletePostForm(request.POST)
        if delete_form.is_valid() and delete_form.cleaned_data['confirm']:
            post.delete()
            return redirect('blog:index')
    else:
        delete_form = DeletePostForm()
    return render(request, 'blog/detail.html', {'post': post, 'delete_form': delete_form, 'comments': comments})



@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id, author=request.user)
    if request.method == 'GET':
        comment.delete()
        return redirect('blog:post_detail', pk=post_id)
    comments = Comment.objects.filter(post_id=post_id)
    post = get_object_or_404(get_posts(), pk=post_id)
    form = PostForm(instance=post)
    return render(request, 'blog/detail.html', {'post': post, 'form': form, "comments": comments})