from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse_lazy
from django.views.generic.edit import CreateView

from users.forms import UserCreationForm

handler404 = "blogicum.views.page_not_found"
handler500 = "blogicum.views.server_error"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("pages/", include("pages.urls", namespace="pages")),
    path("profile/", include("blog.urls", namespace="profile")),
    path("", include("blog.urls", namespace="blog")),
    path("auth/", include("django.contrib.auth.urls")),
    path(
        "auth/registration/",
        CreateView.as_view(
            template_name="registration/registration_form.html",
            form_class=UserCreationForm,
            success_url=reverse_lazy("blog:index"),
        ),
        name="registration",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
