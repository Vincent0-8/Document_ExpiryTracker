from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser


class LoginForm(AuthenticationForm):
    """Form login dengan styling custom."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'field-input',
            'placeholder': 'Username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'field-input',
            'placeholder': 'Password',
        })
    )


class OTPVerifyForm(forms.Form):
    """Form input 6 digit OTP."""

    token = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'field-input otp-input',
            'placeholder': '000000',
            'maxlength': '6',
            'inputmode': 'numeric',
            'autocomplete': 'one-time-code',
        }),
        label='Kode OTP'
    )

    def clean_token(self):
        token = self.cleaned_data.get('token', '').strip()
        if not token.isdigit():
            raise forms.ValidationError('Kode OTP harus berupa angka.')
        return token


class UserCreateForm(forms.ModelForm):
    """Form tambah pengguna baru — hanya Admin."""

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'field-input',
            'placeholder': 'Minimal 8 karakter',
        })
    )
    password2 = forms.CharField(
        label='Konfirmasi Password',
        widget=forms.PasswordInput(attrs={
            'class': 'field-input',
            'placeholder': 'Ulangi password',
        })
    )

    class Meta:
        model  = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email',
                  'role', 'phone_number']
        widgets = {
            'username':     forms.TextInput(attrs={'class': 'field-input'}),
            'first_name':   forms.TextInput(attrs={'class': 'field-input'}),
            'last_name':    forms.TextInput(attrs={'class': 'field-input'}),
            'email':        forms.EmailInput(attrs={'class': 'field-input'}),
            'role':         forms.Select(attrs={'class': 'field-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'field-input'}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Password tidak cocok.')
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """Form edit pengguna — hanya Admin."""

    class Meta:
        model  = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email',
                  'role', 'phone_number', 'is_active']
        widgets = {
            'username':     forms.TextInput(attrs={'class': 'field-input'}),
            'first_name':   forms.TextInput(attrs={'class': 'field-input'}),
            'last_name':    forms.TextInput(attrs={'class': 'field-input'}),
            'email':        forms.EmailInput(attrs={'class': 'field-input'}),
            'role':         forms.Select(attrs={'class': 'field-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'field-input'}),
        }