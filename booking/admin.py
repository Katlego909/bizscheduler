from django.contrib import admin
from .models import Service, Availability, Booking, Payment

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'duration', 'price', 'is_active')
    list_filter = ('vendor', 'is_active')
    search_fields = ('name',)

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'weekday', 'start_time', 'end_time')
    list_filter = ('vendor', 'weekday')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'service', 'date', 'time', 'status')
    list_filter = ('vendor', 'service', 'status', 'date')
    search_fields = ('customer_name', 'customer_email')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'method', 'status', 'created_at')
    list_filter = ('method', 'status')
    search_fields = ('reference',)
