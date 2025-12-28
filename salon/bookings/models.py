from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from staff.models import Master, Service


User = get_user_model()


class ClientPreference(models.Model):
    """Предпочтения клиента по мастерам (необязательно, но масштабируемо)"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Клиент',
        related_name='preference'
    )
    preferred_masters = models.ManyToManyField(
        Master,
        verbose_name='Предпочтительные мастера',
        blank=True
    )

    class Meta:
        verbose_name = 'предпочтение клиента'
        verbose_name_plural = 'Предпочтения клиентов'

    def __str__(self):
        return f'Предпочтения: {self.user}'


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждена'),
        ('cancelled', 'Отменена'),
        ('completed', 'Завершена'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Клиент',
        related_name='bookings'
    )
    master = models.ForeignKey(
        Master,
        on_delete=models.PROTECT,
        verbose_name='Мастер',
        related_name='bookings'
    )
    visit_datetime = models.DateTimeField(
        verbose_name='Дата и время визита'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создана'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлена'
    )

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'Записи'
        ordering = ('-visit_datetime',)
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['master', 'visit_datetime']),
        ]

    def __str__(self):
        return f'{self.user} → {self.master} ({self.visit_datetime:%d.%m.%Y %H:%M})'

    @property
    def total_cost(self):
        return sum(bs.price_at_booking for bs in self.booking_services.all())

    def cancel(self):
        self.status = 'cancelled'
        self.save(update_fields=['status', 'updated_at'])

    # === ВАЛИДАЦИЯ ===
    def clean(self):
        super().clean()

        if not self.master.is_published:
            self.add_error('master', 'Этот мастер временно недоступен.')

        if self.visit_datetime and self.visit_datetime < timezone.now():
            self.add_error('visit_datetime', 'Нельзя записаться на прошедшее время.')

        if self.pk is None:
            return

        if self.visit_datetime and self.master_id:
            duration = sum(
                ms.duration_minutes 
                for ms in self.master.offered_services.filter(
                    service__in=self.booking_services.values_list('service_id', flat=True)
                )
            ) or 60

            start = self.visit_datetime
            end = start + timezone.timedelta(minutes=duration)

            overlapping = Booking.objects.filter(
                master=self.master,
                status__in=['pending', 'confirmed'],
                visit_datetime__lt=end,
                visit_datetime__gt=start - timezone.timedelta(minutes=duration)
            ).exclude(pk=self.pk)  # исключаем текущую запись

            if overlapping.exists():
                self.add_error('visit_datetime', 'У мастера уже есть запись в это время. Выберите другое время.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BookingService(models.Model):
    """Связь «запись — услуга» (одна запись → много услуг)"""
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        verbose_name='Запись',
        related_name='booking_services'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        verbose_name='Услуга',
        related_name='booking_services'
    )
    # можно добавить: цена на момент записи (на случай изменения прайса)
    price_at_booking = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Цена на момент записи',
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'услуга в записи'
        verbose_name_plural = 'Услуги в записях'
        unique_together = ('booking', 'service')

    def __str__(self):
        return f'{self.booking} — {self.service}'
    
    def clean(self):
        super().clean()
        if not self.booking.master.offered_services.filter(service=self.service).exists():
            raise ValidationError(
                f'Мастер {self.booking.master} не оказывает услугу "{self.service}".'
            )
            self.add_error('master', 'У мастера уже есть запись в это время. Выберите другое время.')
        

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)
