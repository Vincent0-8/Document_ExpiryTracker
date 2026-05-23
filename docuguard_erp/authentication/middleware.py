"""
authentication/middleware.py

OTPMiddleware — memastikan setiap request yang masuk:
1. Kalau belum login → boleh akses URL publik saja (login, otp)
2. Kalau sudah login tapi belum OTP verified → paksa ke otp_verify
3. Kalau sudah login + OTP verified → lanjut normal

Dengan middleware ini, anggota lain (Jacky, Vincent, dll.)
TIDAK perlu menambahkan OTPRequiredMixin ke setiap view mereka.
Middleware ini berjalan global untuk seluruh project.
"""

from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.contrib import messages


# URL yang boleh diakses tanpa login sama sekali
PUBLIC_URLS = [
    'authentication:login',
    'authentication:otp_verify',
    'authentication:otp_setup',
    'authentication:logout',
]

# URL prefix yang selalu diizinkan (admin django, static, media)
PUBLIC_URL_PREFIXES = [
    '/admin/',
    '/static/',
    '/media/',
]


class OTPMiddleware:
    """
    Middleware global untuk memaksa OTP verification.

    Cara aktifkan: tambahkan ke MIDDLEWARE di settings.py:
    'authentication.middleware.OTPMiddleware',
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Resolve URL saat ini
        current_path = request.path_info

        # 1. Izinkan URL dengan prefix publik (admin, static, media)
        for prefix in PUBLIC_URL_PREFIXES:
            if current_path.startswith(prefix):
                return self.get_response(request)

        # 2. Resolve nama URL saat ini
        try:
            resolved = resolve(current_path)
            current_url_name = f"{resolved.namespace}:{resolved.url_name}" if resolved.namespace else resolved.url_name
        except Exception:
            return self.get_response(request)

        # 3. Izinkan URL publik tanpa cek
        if current_url_name in PUBLIC_URLS:
            return self.get_response(request)

        # 4. Kalau belum login → redirect ke login
        if not request.user.is_authenticated:
            return redirect(f"{reverse('authentication:login')}?next={current_path}")

        # 5. Sudah login tapi belum OTP verified → paksa OTP
        if not request.session.get('otp_verified', False):
            # Kalau OTP belum pernah di-setup, ke halaman setup
            if not request.user.is_otp_enabled:
                return redirect('authentication:otp_setup')
            messages.warning(request, 'Silakan verifikasi OTP untuk melanjutkan.')
            return redirect('authentication:otp_verify')

        # 6. Semua aman → lanjut
        return self.get_response(request)
