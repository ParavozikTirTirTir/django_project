from django.shortcuts import render
from django.views.generic import TemplateView
from staff.models import Master, Service
from django.db.models import Avg, Count


class HomeView(TemplateView):
    """Главная страница: приветствие + блоки с мастерами и услугами"""
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Топ-3 мастера (по количеству записей)
        context['featured_masters'] = Master.objects.filter(
            is_published=True
        ).annotate(
            booking_count=Count('bookings')
        ).order_by('-booking_count')[:3]
        
        # Популярные услуги (по количеству выборов)
        context['popular_services'] = Service.objects.filter(
            is_published=True
        ).annotate(
            booking_count=Count('booking_services')
        ).order_by('-booking_count')[:4]
        
        # Статистика
        context['stats'] = {
            'total_masters': Master.objects.filter(is_published=True).count(),
            'total_services': Service.objects.filter(is_published=True).count(),
            'avg_price': Service.objects.aggregate(Avg('price'))['price__avg'] or 0,
        }
        return context


class AboutView(TemplateView):
    """О салоне — переименовано из AboutTemplateView"""
    template_name = 'pages/about.html'


class ContactsView(TemplateView):
    """Контакты — новый шаблон"""
    template_name = 'pages/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['address'] = 'г. Москва, ул. Цветочная, д. 15'
        context['phone'] = '+7 (495) 123-45-67'
        context['email'] = 'info@salon.ru'
        context['work_hours'] = {
            'mon_fri': '10:00–21:00',
            'sat': '10:00–20:00',
            'sun': '11:00–19:00'
        }
        return context


# Обработчики ошибок
def permission_denied(request, exception):
    return render(request, "pages/403.html", status=403)


def csrf_failure(request, reason=""):
    return render(request, "pages/403csrf.html", status=403)


def page_not_found(request, exception):
    return render(request, "pages/404.html", status=404)


def server_error(request):
    return render(request, "pages/500.html", status=500)
