from django import forms
from django.contrib.auth.models import User

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ["created_at", "author", "status", "updated_at"]
        widgets = {
            "pub_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]


class DeletePostForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="Подтвердите удаление")
