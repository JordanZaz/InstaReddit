from django import template
from gorl.models import Like


register = template.Library()


@register.filter
def likes(user, post):
    return Like.objects.filter(user_id=user, post_id=post).exists()
