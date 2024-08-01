from django.urls import path

from .views import category_posts, index, post_detail, create_post, profile

app_name = "blog"

urlpatterns = [
    path("", index, name="index"),
    path("posts/<int:pk>/", post_detail,
         name="post_detail"),
    path("category/<slug:category_slug>/", category_posts,
         name="category_posts"),
    path("posts/create/", create_post, name="create_post"),
    path('profile/<str:username>/', profile, name='profile'),
]
