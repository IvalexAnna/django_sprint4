from django.db.models import Count, Q
from django.utils import timezone

from .const import PAGINATE_BY
from .models import Post


class PostListMixin:
    model = Post
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return (
            self.model.objects.filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True,
            )
            .annotate(
                comment_count=Count("comments",
                                    filter=Q(comments__is_published=True))
            )
            .order_by("-pub_date")
            .select_related()
        )
