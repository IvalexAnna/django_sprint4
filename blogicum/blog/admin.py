from django.contrib import admin

from .models import Category, Comment, Location, Post

admin.site.empty_value_display = "Не задано"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "title", "description", "slug", "is_published", "created_at")
    list_editable = ("is_published",)
    search_fields = ("title",)
    list_filter = ("slug",)
    list_display_links = ("title",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published", "created_at")
    list_editable = ("is_published",)
    search_fields = ("name",)
    list_display_links = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "text",
        "pub_date",
        "is_published",
        "created_at",
        "author",
        "category",
        "location",
    )
    list_editable = ("is_published", "category")
    search_fields = ("title",)
    list_filter = ("category",)
    list_display_links = ("title",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "author",
        "is_published",
    )
    list_editable = ("is_published",)
    list_filter = ("post",)
