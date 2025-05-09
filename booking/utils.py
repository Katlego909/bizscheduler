# booking/utils.py

from datetime import datetime, timedelta, time
from django.utils import timezone
from .models import Availability, Booking

def compute_available_slots(vendor, target_date, slot_length=30):
    """
    Return a list of available time slots on target_date for the given vendor.
    Slots are returned as 24‑hour "HH:MM" strings.
    """
    weekday = target_date.weekday()  # 0=Monday, 6=Sunday

    # 1) Fetch all availability windows for that weekday
    windows = Availability.objects.filter(vendor=vendor, weekday=weekday)

    # 2) Fetch already‐booked times on that date
    booked_times = set(
        b.time for b in Booking.objects.filter(vendor=vendor, date=target_date)
    )

    slots = []
    for window in windows:
        # Combine date + time
        start_dt = datetime.combine(target_date, window.start_time)
        end_dt   = datetime.combine(target_date, window.end_time)

        # Step through in slot_length minutes
        current = start_dt
        while current + timedelta(minutes=slot_length) <= end_dt:
            t = current.time()
            # Only include if not already booked
            if t not in booked_times:
                slots.append(t.strftime("%H:%M"))
            current += timedelta(minutes=slot_length)

    return slots


def is_date_available(vendor, target_date):
    """
    Return True if the vendor has any availability windows AND at least one free slot
    on the target_date.
    """
    # If no availability windows, not available
    if not Availability.objects.filter(vendor=vendor, weekday=target_date.weekday()).exists():
        return False

    # If compute_available_slots yields any slots, it's available
    return bool(compute_available_slots(vendor, target_date))


def next_available_dates(vendor, days=14):
    """
    Return a list of dates (date objects) over the next `days` days
    where the vendor has at least one free slot.
    """
    today = timezone.localdate()
    available = []
    for i in range(days):
        d = today + timedelta(days=i)
        if is_date_available(vendor, d):
            available.append(d)
    return available





# Email sending function

