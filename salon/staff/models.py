from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator


class PublishedModel(models.Model):
    """Абстрактная модель с флагом публикации и датой создания."""
    is_published = models.BooleanField(
        verbose_name='Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть.'
    )
    created_at = models.DateTimeField(
        verbose_name='Добавлено',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class Service(PublishedModel):
    """Услуга (стрижка, окрашивание и т.д.)"""
    title = models.CharField(
        max_length=256,
        verbose_name='Название услуги'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Цена',
        validators=[MinValueValidator(0)]
    )
    duration_minutes = models.PositiveSmallIntegerField(
        verbose_name='Длительность (мин)',
        help_text='Сколько времени занимает услуга'
    )

    class Meta:
        verbose_name = 'услуга'
        verbose_name_plural = 'Услуги'
        ordering = ('title',)

    def __str__(self):
        return f'{self.title} — {self.price} ₽'

    def get_absolute_url(self):
        return reverse('staff:service_detail', kwargs={'pk': self.pk})


class Master(PublishedModel):
    """Мастер парикмахерской"""
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия'
    )
    photo = models.ImageField(
        verbose_name='Фото',
        upload_to='masters/',
        blank=True
    )
    services = models.ManyToManyField(
        Service,
        through='MasterService',
        verbose_name='Услуги',
        related_name='masters'
    )

    class Meta:
        verbose_name = 'мастер'
        verbose_name_plural = 'Мастера'
        ordering = ('last_name', 'first_name')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_absolute_url(self):
        return reverse('staff:master_detail', kwargs={'pk': self.pk})


class MasterService(models.Model):
    """Связь «мастер — услуга» с индивидуальным временем выполнения"""
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        verbose_name='Мастер',
        related_name='offered_services'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name='Услуга',
        related_name='provided_by_masters'
    )
    duration_minutes = models.PositiveSmallIntegerField(
        verbose_name='Время выполнения (мин)',
        help_text='Индивидуальное время для этого мастера'
    )

    class Meta:
        verbose_name = 'услуга мастера'
        verbose_name_plural = 'Услуги мастеров'
        unique_together = ('master', 'service')

    def __str__(self):
        return f'{self.master} → {self.service} ({self.duration_minutes} мин)'