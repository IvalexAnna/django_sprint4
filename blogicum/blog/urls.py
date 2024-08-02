from django.urls import path

from .views import category_posts, index, post_detail, create_post, profile, add_comment, edit_comment, edit_post, delete_post, delete_comment

app_name = "blog"

urlpatterns = [
    path("", index, name="index"),
    path("posts/<int:pk>/", post_detail,
         name="post_detail"),
    path("category/<slug:category_slug>/", category_posts,
         name="category_posts"),
    path("posts/create/", create_post, name="create_post"),
    path('profile/<str:username>/', profile, name='profile'),
    path('posts/<int:post_id>/comment/', add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', edit_comment, name='edit_comment'),
    path('posts/<int:post_id>/edit/', edit_post, name="edit_post"),
    path('posts/<int:post_id>/delete', delete_post, name="delete_post"),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/', delete_comment, name='delete_comment')
]
