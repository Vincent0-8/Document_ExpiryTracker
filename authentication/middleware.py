from django.shortcuts import redirect
from django.urls import reverse


class OTPMiddleware:
    """
    Middleware global — pastikan setiap request sudah OTP verified.
    Kecuali halaman login, OTP setup, dan OTP verify.
    """

    EXEMPT_URLS = [
        '/auth/login/',
        '/auth/logout/',
        '/auth/otp/setup/',
        '/auth/otp/verify/',
        '/admin/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Cek apakah URL ini dikecualikan
        path = request.path_info
        is_exempt = any(path.startswith(url) for url in self.EXEMPT_URLS)

        if not is_exempt and request.user.is_authenticated:
            if not request.session.get('otp_verified'):
                return redirect('authentication:otp_verify')

        response = self.get_response(request)
        return response