from django.urls import path

from .views import AboutView, Error403View, Error404View
from .views import Error500View, RulesView

app_name = "pages"

urlpatterns = [
    path("about/", AboutView.as_view(), name="about"),
    path("rules/", RulesView.as_view(), name="rules"),
    path("404/", Error404View.as_view(), name="error_404"),
    path("500/", Error500View.as_view(), name="error_500"),
    path("403/", Error403View.as_view(), name="403csrf"),
]
