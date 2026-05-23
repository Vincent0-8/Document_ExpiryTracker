from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from .models import CustomUser


# ─────────────────────────────────────────────
# LOGIN FORM
# ─────────────────────────────────────────────

class LoginForm(AuthenticationForm):
    """
    Custom login form dengan styling Bootstrap.
    Extends AuthenticationForm bawaan Django.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True,
            'autocomplete': 'username',
        }),
        label='Username'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        }),
        label='Password'
    )


# ─────────────────────────────────────────────
# OTP FORM
# ─────────────────────────────────────────────

class OTPVerifyForm(forms.Form):
    """Form untuk input kode OTP 6 digit."""
    token = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': '000000',
            'autocomplete': 'one-time-code',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}',
            'maxlength': '6',
        }),
        label='Kode OTP (6 digit)',
    )

    def clean_token(self):
        token = self.cleaned_data.get('token', '').strip()
        if not token.isdigit():
            raise ValidationError('Kode OTP hanya boleh berisi angka.')
        if len(token) != 6:
            raise ValidationError('Kode OTP harus tepat 6 digit.')
        return token


# ─────────────────────────────────────────────
# USER MANAGEMENT FORMS (hanya Admin)
# ─────────────────────────────────────────────

class UserCreateForm(UserCreationForm):
    """Form untuk Admin membuat user baru dengan role."""

    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Depan'}),
        label='Nama Depan'
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Belakang'}),
        label='Nama Belakang'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
        label='Email'
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '08xxxxxxxxxx'}),
        label='Nomor HP'
    )
    role = forms.ChoiceField(
        choices=CustomUser.Role.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Role Pengguna'
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name',
            'email', 'phone_number', 'role',
            'password1', 'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Styling field bawaan UserCreationForm
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'username_unik',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password minimal 8 karakter',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ulangi password',
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Email ini sudah digunakan oleh pengguna lain.')
        return email


class UserUpdateForm(UserChangeForm):
    """Form untuk Admin mengedit user yang sudah ada."""

    password = None  # Sembunyikan field password hash dari form edit

    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nama Depan'
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nama Belakang'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label='Email'
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nomor HP'
    )
    role = forms.ChoiceField(
        choices=CustomUser.Role.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Role Pengguna'
    )
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Akun Aktif'
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name',
            'email', 'phone_number', 'role', 'is_active',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Exclude user yang sedang diedit sendiri
        qs = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Email ini sudah digunakan oleh pengguna lain.')
        return email
