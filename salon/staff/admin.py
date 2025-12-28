from django.contrib import admin
from .models import Service, Master, MasterService


class MasterServiceInline(admin.TabularInline):
    model = MasterService
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'duration_minutes', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('is_published',)
    search_fields = ('title',)


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'is_published', 'services_list')
    list_editable = ('is_published',)
    list_filter = ('is_published',)
    search_fields = ('first_name', 'last_name')
    inlines = [MasterServiceInline]
    readonly_fields = ('created_at',)

    def full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'
    full_name.short_description = 'Мастер'

    def services_list(self, obj):
        return ", ".join(s.title for s in obj.services.all()[:3])
    services_list.short_description = 'Услуги'
