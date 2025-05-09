from django import forms
from .models import Booking, Payment, Availability, Service, VendorProfile
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from vendor.models import User

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'service',
            'customer_name',
            'customer_email',
            'customer_phone',
            'date',
            'time',
            'notes'
        ]
        widgets = {
            'service': forms.Select(attrs={'class': 'form-select'}),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your name'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'you@example.com'
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Optional phone number'
            }),
            'date': forms.HiddenInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
            # Hide the default time input entirely:
            'time': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Any special requests or notes?'
            }),
        }

    def __init__(self, *args, vendor=None, **kwargs):
        super().__init__(*args, **kwargs)
        if vendor:
            self.fields['service'].queryset = Service.objects.filter(
                vendor=vendor, is_active=True
            )

    def clean_date(self):
        date = self.cleaned_data['date']
        vendor = getattr(self, 'vendor', None)
        if vendor:
            slots = compute_available_slots(vendor, date)
            if not slots:
                raise forms.ValidationError(
                    "Sorry, this vendor isn’t available on that date. Please choose another day."
                )
        return date        

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['method', 'reference']
        widgets = {
            'method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'EFT ref or leave blank for card'
            }),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Service name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Describe this service'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'placeholder': 'Duration in minutes'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 0,
                'step': '0.01',
                'placeholder': 'Price (e.g. 49.99)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }

class MeetingDetailsForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['meeting_url', 'meeting_details']
        widgets = {
            'meeting_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://meet.example.com/your-link'
            }),
            'meeting_details': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Agenda or notes…'
            }),
        }

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['weekday','start_time','end_time']
        widgets = {
            'weekday': forms.Select(attrs={'class':'form-select'}),
            'start_time': forms.TimeInput(attrs={'type':'time','class':'form-input'}),
            'end_time':   forms.TimeInput(attrs={'type':'time','class':'form-input'}),
        }

class GuestEmailForm(forms.Form):
    guest_email = forms.EmailField(
        label="Enter your email to receive a booking link",
        widget=forms.EmailInput(attrs={'class':'form-input','placeholder':'you@example.com'}),
    )        