from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.BookingCreateView.as_view(), name='create'),
    path('my/', views.MyBookingsView.as_view(), name='my_bookings'),
    path('<int:pk>/cancel/', views.BookingCancelView.as_view(), name='cancel'),
    path('update-services/', views.update_services, name='update_services'),
]
