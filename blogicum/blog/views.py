from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, EditProfileForm, PostForm
from .mixins import PostListMixin
from .models import Category, Comment, Post

User = get_user_model()


class PostListView(PostListMixin, ListView):
    template_name = "blog/index.html"


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"

    def get_object(self, **kwargs):
        queryset = Post.objects.all()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
            )
        else:
            queryset = queryset.filter(
                Q(author__username=self.request.user.username)
                | (
                    Q(is_published=True)
                    & Q(category__is_published=True)
                    & Q(pub_date__lte=timezone.now())
                )
            )
        post = get_object_or_404(queryset, pk=self.kwargs["post_id"])
        if post.status == "scheduled" and post.author != self.request.user:
            return redirect("pages:error_404")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = Comment.objects.filter(
            post_id=self.kwargs["post_id"], is_published=True
        ).select_related("author")
        context["form"] = CommentForm()
        return context


class CategoryPostListView(PostListMixin, ListView):
    template_name = "blog/category.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        return queryset.filter(category=category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(
            Category, slug=self.kwargs["category_slug"]
        )
        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        if post.pub_date <= timezone.now():
            post.status = "published"
        else:
            post.status = "scheduled"
        post.save()
        return redirect("blog:profile", username=self.request.user.username)


class EditPostView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        return redirect("blog:post_detail", post_id=self.kwargs["post_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class DeletePostView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def test_func(self):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        return post.author == self.request.user

    def handle_no_permission(self):
        return redirect("blog:post_detail", post_id=self.kwargs["post_id"])

    def get_success_url(self):
        return reverse("blog:profile", kwargs={"username": self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context["form"] = self.get_form(instance=post)
        return context


class ProfileView(PostListMixin, ListView):
    template_name = "blog/profile.html"

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        if self.request.user == user:
            return (
                Post.objects.filter(author=user)
                .annotate(
                    comment_count=Count(
                        "comments", filter=Q(comments__is_published=True)
                    )
                )
                .order_by("-pub_date")
                .select_related()
            )
        return super().get_queryset().filter(author=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs["username"])
        context["profile"] = user
        return context


@method_decorator(login_required, name="dispatch")
class EditProfileView(View):
    def get(self, request):
        form = EditProfileForm(instance=request.user)
        return render(request, "blog/user.html", {"form": form})

    def post(self, request):
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("blog:profile", username=request.user.username)
        return render(request, "blog/user.html", {"form": form})


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/detail.html"

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        comment = form.save(commit=False)
        comment.post = post
        comment.author = self.request.user
        comment.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"post_id": self.kwargs["post_id"]})


class EditCommentView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/create.html"

    def get_object(self):
        return get_object_or_404(
            Comment,
            id=self.kwargs["comment_id"],
            post_id=self.kwargs["post_id"],
            author=self.request.user,
        )

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"post_id": self.kwargs["post_id"]})


class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = "blog/comment.html"

    def get_object(self):
        return get_object_or_404(
            Comment,
            id=self.kwargs["comment_id"],
            post_id=self.kwargs["post_id"],
            author=self.request.user,
        )

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"post_id": self.kwargs["post_id"]})
