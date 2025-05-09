# vendor/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, VendorProfile

class RegisterForm(UserCreationForm):
    ROLE_CHOICES = [('vendor', 'Vendor'), ('client', 'Client')]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-radio'})
    )
    business_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Business name (vendors only)'
        })
    )
    contact_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Business email'
        })
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Phone number'
        })
    )
    logo = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-input'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 3,
            'placeholder': 'Business address'
        })
    )
    password1 = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = User
        fields = [
            'username', 'email',
            'password1', 'password2',
            'role',
            'business_name', 'contact_email',
            'phone', 'logo', 'address',
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'you@example.com'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-input',
                'placeholder': 'Password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-input',
                'placeholder': 'Confirm Password'
            }),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data['role']
        user.is_vendor = (role == 'vendor')
        user.is_client = (role == 'client')
        if commit:
            user.save()
            if user.is_vendor:
                VendorProfile.objects.create(
                    user=user,
                    business_name=self.cleaned_data['business_name'],
                    contact_email=self.cleaned_data['contact_email'],
                    phone=self.cleaned_data['phone'],
                    logo=self.cleaned_data.get('logo'),
                    address=self.cleaned_data['address']
                )
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username or Email',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username or Email'
        })
    )
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # allow login by username or email
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=username)
                except User.DoesNotExist:
                    raise forms.ValidationError("Invalid login credentials.")
            if not user.check_password(password):
                raise forms.ValidationError("Invalid login credentials.")

        return cleaned_data

