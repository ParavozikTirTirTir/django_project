from django.views.generic import ListView, DetailView
from .models import Master, Service

class MasterListView(ListView):
    model = Master
    template_name = 'staff/master_list.html'
    context_object_name = 'masters'
    queryset = Master.objects.filter(is_published=True)

class MasterDetailView(DetailView):
    model = Master
    template_name = 'staff/master_detail.html'
    context_object_name = 'master'

    def get_queryset(self):
        return Master.objects.select_related().prefetch_related(
            'offered_services__service'  # здесь делаем JOIN к услугам
        )

class ServiceListView(ListView):
    model = Service
    template_name = 'staff/service_list.html'
    context_object_name = 'services'
    queryset = Service.objects.filter(is_published=True)

class ServiceDetailView(DetailView):
    model = Service
    template_name = 'staff/service_detail.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.object

        masters_with_time = []
        # Используем НОВОЕ имя: provided_by_masters
        for ms in service.provided_by_masters.select_related('master'):
            masters_with_time.append({
                'master': ms.master,
                'duration_minutes': ms.duration_minutes
            })
        
        context['masters_with_time'] = masters_with_time
        return context
