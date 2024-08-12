from django.urls import path

from .views import (AddCommentView, CategoryPostListView, CreatePostView,
                    DeleteCommentView, DeletePostView, EditCommentView,
                    EditPostView, EditProfileView, PostDetailView,
                    PostListView, ProfileView)

app_name = "blog"


urlpatterns = [
    path("", PostListView.as_view(), name="index"),
    path("posts/<int:pk>/",
         PostDetailView.as_view(),
         name="post_detail"),
    path(
        "category/<slug:category_slug>/",
        CategoryPostListView.as_view(),
        name="category_posts",
    ),
    path("posts/create/",
         CreatePostView.as_view(),
         name="create_post"),
    path("profile/<str:username>/",
         ProfileView.as_view(),
         name="profile"),
    path(
        "posts/<int:post_id>/comment/add/",
        AddCommentView.as_view(),
        name="add_comment"
    ),
    path(
        "posts/<int:post_id>/comment/<int:comment_id>/edit/",
        EditCommentView.as_view(),
        name="edit_comment",
    ),
    path("posts/<int:post_id>/edit/",
         EditPostView.as_view(),
         name="edit_post"),
    path("posts/<int:post_id>/delete/",
         DeletePostView.as_view(),
         name="delete_post"),
    path(
        "posts/<int:post_id>/comment/<int:comment_id>/delete_comment/",
        DeleteCommentView.as_view(),
        name="delete_comment",
    ),
    path("edit_profile/",
         EditProfileView.as_view(),
         name="edit_profile"),
]
