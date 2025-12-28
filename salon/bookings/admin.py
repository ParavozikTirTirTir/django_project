from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db import models
from .models import ClientPreference, Booking, BookingService


class BookingServiceInline(admin.TabularInline):
    model = BookingService
    extra = 1
    readonly_fields = ('price_at_booking',)
    fields = ('service', 'price_at_booking')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Подсказка в форме
        formset.form.base_fields['service'].widget.attrs['style'] = 'width: 200px;'
        return formset


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user_link',
        'master_link',
        'visit_datetime',
        'status_badge',
        'total_cost_display',
        'created_at'
    )
    list_filter = (
        'status',
        'master',
        ('visit_datetime', admin.DateFieldListFilter),
        'created_at'
    )
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'master__first_name',
        'master__last_name'
    )
    date_hierarchy = 'visit_datetime'
    inlines = [BookingServiceInline]
    actions = ['mark_confirmed', 'mark_cancelled', 'mark_completed']

    fieldsets = (
        ('Основное', {
            'fields': ('user', 'master', 'visit_datetime')
        }),
        ('Статус', {
            'fields': ('status',),
            'classes': ('collapse',)
        }),
    )

    # Сортировка в форме
    ordering = ('-visit_datetime',)

    # === Кастомные методы отображения ===

    def user_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.username)
    user_link.short_description = 'Клиент'
    user_link.admin_order_field = 'user__last_name'

    def master_link(self, obj):
        url = reverse('admin:staff_master_change', args=[obj.master.id])
        return format_html('<a href="{}">{}</a>', url, obj.master)
    master_link.short_description = 'Мастер'
    master_link.admin_order_field = 'master__last_name'

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',      # жёлтый
            'confirmed': '#28a745',    # зелёный
            'cancelled': '#dc3545',    # красный
            'completed': '#17a2b8',    # синий
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Статус'

    def total_cost_display(self, obj):
        return f"{obj.total_cost} ₽"
    total_cost_display.short_description = 'Стоимость'
    total_cost_display.admin_order_field = 'booking_services__service__price'

    # === Действия (actions) ===

    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'Подтверждено {updated} записей.')
    mark_confirmed.short_description = '✅ Подтвердить выбранные записи'

    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'Отменено {updated} записей.')
    mark_cancelled.short_description = '❌ Отменить выбранные записи'

    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'Завершено {updated} записей.')
    mark_completed.short_description = '✔️ Завершить выбранные записи'

    # Защита от массового изменения статуса «Завершена» без даты в прошлом
    mark_completed.allowed_permissions = ('change',)


@admin.register(ClientPreference)
class ClientPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_masters_list')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    filter_horizontal = ('preferred_masters',)

    def preferred_masters_list(self, obj):
        return ", ".join(str(m) for m in obj.preferred_masters.all()[:3])
    preferred_masters_list.short_description = 'Предпочтительные мастера'
