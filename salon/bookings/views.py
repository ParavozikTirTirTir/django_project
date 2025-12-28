from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView, ListView, TemplateView
)
from django.views.generic.edit import FormView
from django import forms
from django.db import transaction
from django.utils import timezone
import traceback

from staff.models import Master, Service, MasterService
from .models import Booking, BookingService
from .forms import BookingForm
from django.template.loader import render_to_string
from django.http import HttpResponse

class BookingCreateView(LoginRequiredMixin, FormView):
    template_name = 'bookings/booking_form.html'
    form_class = BookingForm
    success_url = reverse_lazy('bookings:my_bookings')

    def form_valid(self, form):
        master = form.cleaned_data['master']
        services = form.cleaned_data['services']
        visit_datetime = form.cleaned_data['visit_datetime']

        try:
            with transaction.atomic():
                booking = Booking(
                    user=self.request.user,
                    master=master,
                    visit_datetime=visit_datetime,
                    status='pending'
                )
                booking.save()

                for service in services:
                    BookingService.objects.create(
                        booking=booking,
                        service=service,
                        price_at_booking=service.price
                    )
        except Exception as e:
            error_msg = f"{e}\n\nTraceback:\n{''.join(traceback.format_tb(e.__traceback__))}"
            messages.error(self.request, f'Ошибка при создании записи: {error_msg}')
            return self.form_invalid(form)

        messages.success(
            self.request,
            f'Запись к {master} на {visit_datetime:%d.%m.%Y %H:%M} создана!'
        )
        return super().form_valid(form)


class MyBookingsView(LoginRequiredMixin, ListView):
    template_name = 'bookings/my_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).select_related('master').prefetch_related(
            'booking_services__service'
        ).order_by('-visit_datetime')


class BookingCancelView(LoginRequiredMixin, TemplateView):
    template_name = 'bookings/booking_confirm_cancel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = get_object_or_404(
            Booking,
            pk=kwargs['pk'],
            user=self.request.user  # только свои записи
        )
        context['booking'] = booking
        return context

    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(
            Booking,
            pk=kwargs['pk'],
            user=request.user
        )
        if booking.status == 'cancelled':
            messages.warning(request, 'Запись уже отменена.')
        else:
            booking.cancel()
            messages.success(request, f'Запись к {booking.master} отменена.')
        return redirect('bookings:my_bookings')


def update_services(request):
    """Возвращает HTML-блок с чекбоксами услуг для выбранного мастера."""
    master_id = request.GET.get('master')
    services_html = '<div class="text-muted">Сначала выберите мастера</div>'
    
    if master_id:
        try:
            master = Master.objects.get(id=master_id, is_published=True)
            # Получаем услуги, которые мастер оказывает
            services = master.services.filter(is_published=True)
            # Рендерим только поле services
            services_html = render_to_string(
                'bookings/partials/_services_field.html',
                {'services': services}
            )
        except Master.DoesNotExist:
            services_html = '<div class="text-danger">Мастер не найден</div>'

    return HttpResponse(services_html)
