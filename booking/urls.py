from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    path('vendors/<slug:slug>/', views.vendor_booking_page, name='vendor_booking'),
    path('vendors/<slug:slug>/guest/<str:guest_token>/', views.vendor_booking_page,name='guest_booking'),
    
    path('simulate-payment/', views.simulate_payment, name='simulate_payment'),

    path('booking-success/<int:booking_id>/', views.booking_success, name='booking_success'),
    
    # Vendor dashboard routes
    path('vendor/bookings/', views.vendor_bookings, name='vendor_bookings'),
    path('vendor/services/', views.vendor_services, name='vendor_services'),
    path('vendor/calendar/', views.vendor_calendar, name='vendor_calendar'),
    path('vendor/services/create/', views.create_service, name='create_service'),

    # Client bookings
    path('my-bookings/', views.client_bookings, name='client_bookings'),
    path('my-bookings/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),


    path('my-bookings/', views.client_bookings, name='client_bookings'),
    path('my-bookings/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    path('vendor/bookings/accept/<int:booking_id>/', views.accept_booking,name='accept_booking'),
    path('vendor/bookings/reject/<int:booking_id>/', views.reject_booking,name='reject_booking'),
    path('vendor/bookings/<int:booking_id>/meeting/', views.edit_meeting, name='edit_meeting'),

    # Availability
    path('availability/', views.manage_availability, name='manage_availability'),
    path('availability/<int:pk>/edit/',   views.edit_availability,   name='edit_availability'),
    path('availability/<int:pk>/delete/', views.delete_availability, name='delete_availability'),
]
