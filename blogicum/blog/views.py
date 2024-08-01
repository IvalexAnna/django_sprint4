from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

from . import const
from .models import Category, Post
from .forms import PostForm


User = get_user_model()


def get_posts():
    print(timezone.now())
    return Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


def get_categories():
    return Category.objects.filter(is_published=True)


def index(request):
    posts = get_posts()
    paginator = Paginator(posts, 10)
    num_pages = request.GET.get('page')
    page_obj = paginator.get_page(num_pages)
    return render(request, "blog/index.html", {"page_obj": page_obj})


def post_detail(request, pk):
    post = get_object_or_404(get_posts(), pk=pk)
    return render(request, "blog/detail.html", {"post": post})


def category_posts(request, category_slug):
    category = get_object_or_404(get_categories(), slug=category_slug)
    posts = category.posts.filter(pub_date__lte=timezone.now(),
                                  is_published=True)
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
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)
    is_owner = request.user == user
    paginator = Paginator(posts, 10)
    num_pages = request.GET.get('page')
    page_obj = paginator.get_page(num_pages)

    return render(request, 'blog/profile.html', {
        'profile_user': user,
        'page_obj': page_obj,
        'is_owner': is_owner,
    })
