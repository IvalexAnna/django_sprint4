from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginRequiredMixin,
    PasswordChangeDoneView,
    PasswordChangeView,
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import UserEditForm

User = get_user_model()


class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:password_change_done")


class ChangePasswordDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "users/password_change_done.html"


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("blog:profile", username=request.user.username)
    else:
        form = UserEditForm(instance=request.user)
    return render(request, "edit_profile.html", {"form": form})
