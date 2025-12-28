from django import template
from ..models import MasterService

register = template.Library()

@register.filter
def duration_for(master, service):
    """Использование: {{ master|duration_for:service }}"""
    ms = MasterService.objects.filter(master=master, service=service).first()
    return ms.duration_minutes if ms else None