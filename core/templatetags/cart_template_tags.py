from django import template
from core.models import Booking

register = template.Library()


@register.filter
def booking_count(user):
    if user.is_authenticated:
        qs = Booking.objects.filter(user=user)
        return len(qs)
    return 0
