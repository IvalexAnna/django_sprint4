from django.urls import include, path

from .views import (
    AddCommentView,
    CategoryPostListView,
    CreatePostView,
    DeleteCommentView,
    DeletePostView,
    EditCommentView,
    EditPostView,
    EditProfileView,
    PostDetailView,
    PostListView,
    ProfileView,
)

app_name = "blog"

posts_urls = [
    path("<int:post_id>/", PostDetailView.as_view(), name="post_detail"),
    path("create/", CreatePostView.as_view(), name="create_post"),
    path("<int:post_id>/comment/add/",
         AddCommentView.as_view(), name="add_comment"),
    path(
        "<int:post_id>/comment/<int:comment_id>/edit/",
        EditCommentView.as_view(),
        name="edit_comment",
    ),
    path("<int:post_id>/edit/", EditPostView.as_view(), name="edit_post"),
    path("<int:post_id>/delete/",
         DeletePostView.as_view(), name="delete_post"),
    path(
        "<int:post_id>/comment/<int:comment_id>/delete_comment/",
        DeleteCommentView.as_view(),
        name="delete_comment",
    ),
]


category_urls = [
    path(
        "<slug:category_slug>/",
        CategoryPostListView.as_view(), name="category_posts"
    ),
]

urlpatterns = [
    path("", PostListView.as_view(), name="index"),
    path("posts/", include(posts_urls)),
    path("category/", include(category_urls)),
    path("profile/<str:username>/", ProfileView.as_view(), name="profile"),
    path("edit_profile/", EditProfileView.as_view(), name="edit_profile"),
]
