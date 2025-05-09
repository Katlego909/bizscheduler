from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import datetime
from .models import Booking, VendorProfile
from .utils import compute_available_slots
from django.core.mail import send_mail



def send_guest_magic_link(vendor: VendorProfile, email: str, full_link: str, expires_hours: int = 24):
    html = render_to_string('emails/guest_magic_link.html', {
        'vendor': vendor,
        'link': full_link,
        'expires_in_hours': expires_hours,
    })
    text = strip_tags(html)
    msg = EmailMultiAlternatives(
        subject=f"Your booking link for {vendor.business_name}",
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email]
    )
    msg.attach_alternative(html, "text/html")
    msg.send()



def send_booking_confirmed_vendor(booking: Booking):
    vendor = booking.vendor
    html = render_to_string('emails/booking_confirmed_vendor.html', {
        'booking': booking,
    })
    text = strip_tags(html)
    msg = EmailMultiAlternatives(
        subject=f"Booking confirmed for {booking.customer_name}",
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[vendor.contact_email],
    )
    msg.attach_alternative(html, "text/html")
    msg.send()


def send_booking_pending_vendor(booking: Booking):
    vendor = booking.vendor
    vendor_email = vendor.contact_email

    if not vendor_email:
        print("❌ Cannot send email: Vendor contact_email is missing.")
        return

    try:
        manage_url = reverse('vendor_bookings')
        html = render_to_string('emails/booking_pending_vendor.html', {
            'booking': booking,
            'manage_url': manage_url,
        })
        text = strip_tags(html)

        msg = EmailMultiAlternatives(
            subject=f"New booking request from {booking.customer_name}",
            body=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[vendor_email],
        )
        msg.attach_alternative(html, "text/html")
        msg.send()

        print(f"✅ Email sent to vendor: {vendor_email}")

    except Exception as e:
        print(f"❌ Failed to send booking email to vendor: {vendor_email}")
        print("   Error:", str(e))


def send_booking_cancelled_vendor(booking: Booking, reason: str = None):
    vendor_email = booking.vendor.contact_email
    html = render_to_string('emails/booking_cancelled_vendor.html', {
        'booking': booking,
        'reason': reason,
    })
    text = strip_tags(html)
    msg = EmailMultiAlternatives(
        subject=f"Booking cancelled for {booking.customer_name}",
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[vendor_email],
    )
    msg.attach_alternative(html, "text/html")
    msg.send()


def send_booking_confirmed_client(booking: Booking):
    client_email = booking.customer_email
    html = render_to_string('emails/booking_confirmed_client.html', {
        'client_name': booking.customer_name,
        'vendor': booking.vendor,
        'service': booking.service,
        'booking': booking,
        'meeting_url': getattr(booking, 'meeting_url', None),
        'meeting_details': getattr(booking, 'meeting_details', None),
    })
    text = strip_tags(html)
    msg = EmailMultiAlternatives(
        subject="Your booking is confirmed",
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[client_email]
    )
    msg.attach_alternative(html, "text/html")
    msg.send()


def send_booking_cancelled_client(booking: Booking, reason: str = None):
    client_email = booking.customer_email
    html = render_to_string('emails/booking_cancelled_client.html', {
        'client_name': booking.customer_name,
        'vendor': booking.vendor,
        'booking': booking,
        'reason': reason,
    })
    text = strip_tags(html)
    msg = EmailMultiAlternatives(
        subject="Your booking was cancelled",
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[client_email]
    )
    msg.attach_alternative(html, "text/html")
    msg.send()


def send_booking_reminder_client(booking: Booking, lead_minutes: int = 30):
    client_email = booking.customer_email
    start_dt = timezone.make_aware(
        datetime.combine(booking.date, booking.time),
        timezone.get_current_timezone()
    )
    delta = start_dt - timezone.now()
    human_delta = f"in {int(delta.total_seconds()//60)} minutes" if delta.total_seconds() > 0 else "soon"
    html = render_to_string('emails/booking_reminder_client.html', {
        'client_name': booking.customer_name,
        'vendor': booking.vendor,
        'booking': booking,
        'time_to_start': human_delta,
        'meeting_url': getattr(booking, 'meeting_url', None),
    })
    text = strip_tags(html)
    msg = EmailMultiAlternatives(
        subject="Reminder: Your appointment is coming up",
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[client_email]
    )
    msg.attach_alternative(html, "text/html")
    msg.send()
