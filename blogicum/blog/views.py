from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, EditProfileForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()


class PostListView(ListView):

    model = Post
    template_name = "blog/index.html"
    context_object_name = "page_obj"
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True,
            )
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"
    context_object_name = "post"

    def get_object(self, **kwargs):
        queryset = Post.objects.all()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_published=True,
                                       category__is_published=True)
        else:
            queryset = queryset.filter(
                Q(author__username=self.request.user.username)
                | (
                    Q(is_published=True)
                    & Q(category__is_published=True)
                    & Q(pub_date__lte=timezone.now())
                )
            )
        post = get_object_or_404(queryset, pk=self.kwargs["pk"])
        if post.status == "scheduled" and post.author != self.request.user:
            return redirect("pages:error_404")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = Comment.objects.filter(post_id=self.kwargs["pk"])
        if self.request.method == "POST":
            context["form"] = CommentForm(self.request.POST)
        else:
            context["form"] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            return redirect("blog:post_detail", pk=self.object.pk)
        return self.render_to_response(self.get_context_data(form=form))


class CategoryPostListView(ListView):
    model = Post
    template_name = "blog/category.html"
    context_object_name = "page_obj"
    paginate_by = 10

    def get_queryset(self):
        category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        return category.posts.filter(pub_date__lte=timezone.now(),
                                     is_published=True)

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


class EditPostView(UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    context_object_name = "post"

    def test_func(self):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        return post.author == self.request.user

    def handle_no_permission(self):
        return redirect("blog:post_detail", pk=self.kwargs["post_id"])

    def get_object(self):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        if post.author != self.request.user:
            return None
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["id_edit"] = True
        context["comments"] = Comment.objects.filter(
            post_id=self.kwargs["post_id"]
        )
        return context

    def form_valid(self, form):
        form.save()
        return redirect("blog:post_detail", pk=self.kwargs["post_id"])


class DeletePostView(UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"
    context_object_name = "post"

    def test_func(self):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        return (self.request.user.is_authenticated
                and post.author == self.request.user)

    def handle_no_permission(self):
        return redirect("blog:post_detail", pk=self.kwargs["post_id"])

    def get_object(self):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        if post.author != self.request.user:
            self.handle_no_permission()
        return post

    def get_success_url(self):
        return reverse("blog:profile",
                       kwargs={"username": self.request.user.username})


class ProfileView(DetailView):
    model = User
    template_name = "blog/profile.html"
    context_object_name = "profile_user"

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context["posts"] = (
            Post.objects.filter(author=user)
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )
        context["profile"] = user
        context["is_owner"] = self.request.user == user
        context["username"] = user.username
        context["date_joined"] = user.date_joined
        paginator = Paginator(context["posts"], 10)
        page = self.request.GET.get("page")
        context["page_obj"] = paginator.get_page(page)
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

        return redirect("blog:post_detail", pk=post.id)


class EditCommentView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/detail.html"

    def get_object(self):
        return get_object_or_404(
            Comment,
            id=self.kwargs["comment_id"],
            post_id=self.kwargs["post_id"],
            author=self.request.user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = Comment.objects.filter(
            post_id=self.kwargs["post_id"])
        context["post"] = get_object_or_404(Post, pk=self.kwargs["post_id"])
        return context

    def form_valid(self, form):
        form.instance.edited_at = timezone.now()
        form.save()
        return redirect("blog:post_detail", pk=self.kwargs["post_id"])


class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = "blog/detail.html"
    context_object_name = "comment"

    def get_object(self):
        return get_object_or_404(
            Comment,
            id=self.kwargs["comment_id"],
            post_id=self.kwargs["post_id"],
            author=self.request.user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = Comment.objects.filter(
            post_id=self.kwargs["post_id"])
        context["post"] = get_object_or_404(Post, pk=self.kwargs["post_id"])
        return context

    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        return redirect("blog:post_detail", pk=self.kwargs["post_id"])
