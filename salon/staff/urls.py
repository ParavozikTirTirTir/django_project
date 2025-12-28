from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # Мастера
    path(
        'masters/',
        views.MasterListView.as_view(),
        name='master_list'
    ),
    path(
        'masters/<int:pk>/',
        views.MasterDetailView.as_view(),
        name='master_detail'
    ),
    
    # Услуги
    path(
        'services/',
        views.ServiceListView.as_view(),
        name='service_list'
    ),
    path(
        'services/<int:pk>/',
        views.ServiceDetailView.as_view(),
        name='service_detail'
    ),
]
