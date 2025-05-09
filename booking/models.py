from django.db import models
from vendor.models import VendorProfile
from django.utils import timezone

# The service(s) a vendor offers
class Service(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.vendor.business_name}"

# Vendor availability (used to generate time slots)
class Availability(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='availabilities')
    # weekday: 0=Monday … 6=Sunday
    weekday = models.IntegerField(choices=[(i, day) for i, day in enumerate(
        ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    )])
    start_time = models.TimeField()
    end_time   = models.TimeField()

    class Meta:
        unique_together = ('vendor', 'weekday', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.vendor.business_name} - {self.get_weekday_display()} {self.start_time} to {self.end_time}"

# Booking made by a client
class Booking(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    meeting_url = models.URLField(blank=True, null=True)
    meeting_details = models.TextField(blank=True, null=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['vendor', 'service', 'date', 'time'],
                name='unique_booking_slot'
            )
        ]

    def __str__(self):
        return f"{self.service.name} - {self.customer_name} on {self.date} at {self.time}"

# Simulated payment tracking
class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=20, choices=[('eft', 'EFT'), ('card', 'Card'), ('cash', 'Cash')])
    reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking} - {self.status}"

