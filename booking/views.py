from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import login, authenticate, logout
from .models import Service, Booking, VendorProfile, Payment, Availability
from .forms import BookingForm, PaymentForm, ServiceForm, MeetingDetailsForm, AvailabilityForm, GuestEmailForm
from vendor.models import VendorProfile 
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, date, datetime
from django.utils.timezone import now
from django.http import HttpResponseForbidden
from .utils import compute_available_slots
from django.core.signing import Signer, BadSignature
from .email_utils import send_booking_pending_vendor, send_guest_magic_link, send_booking_confirmed_client, send_booking_cancelled_client, send_booking_confirmed_vendor, send_booking_cancelled_vendor
from django.core.mail import send_mail

signer = Signer()

def home(request):
    return render(request, 'booking/home.html')

# Public Booking Page
def vendor_booking_page(request, slug, guest_token=None):
    vendor = get_object_or_404(VendorProfile, slug=slug)

    # Build next 7 days
    today = date.today()
    dates = [today + timedelta(days=i) for i in range(7)]

    # Determine selected_date from POST or GET
    selected_iso = request.POST.get('date') or request.GET.get('date')
    try:
        selected_date = date.fromisoformat(selected_iso) if selected_iso else date.today()
    except ValueError:
        selected_date = date.today()

    # Precompute available time slots
    slots = compute_available_slots(vendor, selected_date)

    # Step 1: Guest email capture
    if not request.user.is_authenticated and guest_token is None:
        if request.method == 'POST' and 'guest_email' in request.POST:
            guest_form = GuestEmailForm(request.POST)
            if guest_form.is_valid():
                email = guest_form.cleaned_data['guest_email']
                token = signer.sign(f"{vendor.pk}:{email}")
                link = f"{request.scheme}://{request.get_host()}{reverse('guest_booking', kwargs={'slug': vendor.slug, 'guest_token': token})}?date={selected_date.isoformat()}"
                # TODO: send email with booking link
                send_guest_magic_link(vendor, email, link)
                return render(request, 'booking/guest_email_sent.html', {'email': email})
        else:
            guest_form = GuestEmailForm()
        return render(request, 'booking/guest_email_capture.html', {
            'vendor': vendor,
            'guest_form': guest_form,
        })

    # Step 2: Decode guest token if provided
    guest_email = None
    if guest_token:
        try:
            unsigned = signer.unsign(guest_token)
            vid, guest_email = unsigned.split(":", 1)
            if int(vid) != vendor.pk:
                raise BadSignature()
        except BadSignature:
            return HttpResponseBadRequest("Invalid or expired booking link.")

    # Step 3: Handle form submission
    if request.method == 'POST' and 'customer_name' in request.POST:
        form = BookingForm(request.POST, vendor=vendor)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.vendor = vendor
            booking.date = selected_date
            booking.status = 'pending'

            # Set customer_email based on guest or logged-in user
            if guest_email:
                booking.customer_email = guest_email

            elif request.user.is_authenticated:
                booking.customer_email = request.user.email

            booking.save()

            # Optionally send notification to vendor
            # send_booking_pending_vendor(booking)

            request.session['booking_id'] = booking.id
            return redirect('simulate_payment')

    else:
        # Step 4: Show form with pre-filled data if user is authenticated
        initial = {'date': selected_date}

        if request.user.is_authenticated:
            initial.update({
                'customer_name': request.user.get_full_name() or request.user.username,
                'customer_email': request.user.email,
            })
            # Optional: pull phone from profile
            if hasattr(request.user, 'profile') and getattr(request.user.profile, 'phone', None):
                initial['customer_phone'] = request.user.profile.phone

        form = BookingForm(vendor=vendor, initial=initial)

    return render(request, 'booking/vendor_booking_page.html', {
        'vendor': vendor,
        'form': form,
        'dates': dates,
        'selected_date': selected_date,
        'slots': slots,
        'guest_email': guest_email,
    })

# Simulate Payment
def simulate_payment(request):
    booking_id = request.session.get('booking_id')
    if not booking_id:
        return redirect('register_vendor')
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking

            # Simulate card auto-success
            if payment.method == 'card':
                payment.status = 'success'
            elif payment.method == 'eft':
                payment.status = 'pending'
            payment.save()

            booking.status = 'pending' 
            booking.save()
            send_booking_pending_vendor(booking)
            del request.session['booking_id']
            return redirect('booking_success', booking_id=booking.id)
    else:
        form = PaymentForm()

    return render(request, 'booking/simulate_payment.html', {
        'booking': booking,
        'form': form
    })

# Booking success confirmation
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking/booking_success.html', {'booking': booking})


# Vendor Dashboard View: List of Bookings
@login_required
def vendor_bookings(request):
    vendor = request.user.vendor_profile
    bookings = vendor.bookings.order_by('-created_at')
    return render(request, 'booking/vendor_bookings.html', {'bookings': bookings})

# Vendor Dashboard View: Manage Services
@login_required
def vendor_services(request):
    vendor = request.user.vendor_profile
    services = vendor.services.all()
    return render(request, 'booking/vendor_services.html', {'services': services})

def vendor_calendar(request):
    today = date.today()
    week_dates = [today + timedelta(days=i) for i in range(7)]

    vendor = request.user.vendor_profile

    # Group bookings by date
    bookings_by_day = {
        d: Booking.objects.filter(vendor=vendor, date=d)
        for d in week_dates
    }

    return render(request, 'booking/vendor_calendar.html', {
        'week_dates': week_dates,
        'bookings_by_day': bookings_by_day,
    })

@login_required
def create_service(request):
    vendor = request.user.vendor_profile
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.vendor = vendor
            service.save()
            return redirect('vendor_services')
    else:
        form = ServiceForm()
    return render(request, 'booking/create_service.html', {'form': form})

# Accept or Reject
@login_required
def accept_booking(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        vendor=request.user.vendor_profile
    )
    if booking.status == 'pending':
        booking.status = 'confirmed'
        booking.save()
        send_booking_confirmed_vendor(booking)
        send_booking_confirmed_client(booking)
    return redirect('vendor_bookings')

@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        vendor=request.user.vendor_profile
    )
    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
        send_booking_cancelled_client(booking, reason="Booking rejected by vendor.")
    return redirect('vendor_bookings')

# Clients
@login_required
def client_bookings(request):
    # only show bookings made with their email (and optional account linkage)
    bookings = Booking.objects.filter(
        customer_email=request.user.email
    ).order_by('-date', '-time')
    return render(request, 'booking/client_bookings.html', {
        'bookings': bookings
    })

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer_email=request.user.email)
    if booking.status != 'pending':
        return HttpResponseForbidden("You can only cancel pending bookings.")
    booking.status = 'cancelled'
    booking.save()
    send_booking_cancelled_client(booking, reason="Booking cancelled by client.")
    return redirect('client_bookings')


# Meeting link

@login_required
def edit_meeting(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, vendor=request.user.vendor_profile)
    if request.method == 'POST':
        form = MeetingDetailsForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('vendor_bookings')
    else:
        form = MeetingDetailsForm(instance=booking)
    return render(request, 'booking/edit_meeting.html', {
        'form': form,
        'booking': booking
    })

# Availability

@login_required
def manage_availability(request):
    vendor = request.user.vendor_profile
    availabilities = vendor.availabilities.all()

    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            av = form.save(commit=False)
            av.vendor = vendor
            av.save()
            return redirect('manage_availability')
    else:
        form = AvailabilityForm()

    return render(request, 'booking/manage_availability.html', {
        'availabilities': availabilities,
        'form': form
    })

@login_required
def edit_availability(request, pk):
    av = get_object_or_404(Availability, pk=pk, vendor=request.user.vendor_profile)
    form = AvailabilityForm(request.POST or None, instance=av)
    if form.is_valid():
        form.save()
        return redirect('manage_availability')
    return render(request, 'booking/edit_availability.html', {'form': form})

@login_required
def delete_availability(request, pk):
    av = get_object_or_404(Availability, pk=pk, vendor=request.user.vendor_profile)
    if request.method == 'POST':
        av.delete()
        return redirect('manage_availability')
    return render(request, 'booking/delete_availability.html', {'availability': av})