from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from staff.models import Master, Service, MasterService


class BookingForm(forms.Form):
    """Форма записи клиента: мастер → услуги → время"""
    master = forms.ModelChoiceField(
        queryset=Master.objects.filter(is_published=True),
        label='Мастер',
        empty_label='Выберите мастера',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.none(),
        label='Услуги',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    visit_datetime = forms.DateTimeField(
        label='Дата и время визита',
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # При первом открытии — услуги пустые (нормально!)
        self.fields['services'].queryset = Service.objects.none()

        # Если форма отправлена (POST) — заполняем услуги
        if 'master' in self.data:
            try:
                master_id = int(self.data['master'])
                master = Master.objects.get(id=master_id, is_published=True)
                self.fields['services'].queryset = master.services.filter(is_published=True)
            except (ValueError, Master.DoesNotExist):
                pass

    def clean_master(self):
        master = self.cleaned_data.get('master')
        if master and not master.is_published:
            raise ValidationError('Выбранный мастер временно недоступен.')
        return master

    def clean_visit_datetime(self):
        dt = self.cleaned_data.get('visit_datetime')
        if dt and dt < timezone.now():
            raise ValidationError('Нельзя записаться на прошедшее время.')
        return dt

    def clean(self):
        cleaned_data = super().clean()
        master = cleaned_data.get('master')
        services = cleaned_data.get('services')
        visit_datetime = cleaned_data.get('visit_datetime')

        if not (master and services and visit_datetime):
            return cleaned_data

        # Проверка: услуги должны быть в арсенале мастера
        invalid_services = []
        total_duration = 0

        for service in services:
            try:
                ms = MasterService.objects.get(master=master, service=service)
                total_duration += ms.duration_minutes
            except MasterService.DoesNotExist:
                invalid_services.append(service.title)

        if invalid_services:
            raise ValidationError(
                f'Мастер не оказывает услуги: {", ".join(invalid_services)}.'
            )

        # Проверка пересечения времени
        start = visit_datetime
        end = start + timezone.timedelta(minutes=total_duration)

        from .models import Booking
        overlapping = Booking.objects.filter(
            master=master,
            status__in=['pending', 'confirmed'],
            visit_datetime__lt=end,
            visit_datetime__gt=start - timezone.timedelta(minutes=total_duration)
        )

        # Исключаем текущую запись при редактировании
        if self.initial.get('booking_id'):
            overlapping = overlapping.exclude(pk=self.initial['booking_id'])

        if overlapping.exists():
            raise ValidationError(
                'Выбранное время занято. Попробуйте другое время или другого мастера.'
            )

        # Сохраняем рассчитанную длительность для использования в view
        self.duration_minutes = total_duration
        return cleaned_data
