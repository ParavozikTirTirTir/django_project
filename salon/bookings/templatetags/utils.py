from django import template

register = template.Library()

@register.filter
def status_color(status):
    return {
        'pending': 'warning',
        'confirmed': 'success',
        'cancelled': 'danger',
        'completed': 'info',
    }.get(status, 'secondary')