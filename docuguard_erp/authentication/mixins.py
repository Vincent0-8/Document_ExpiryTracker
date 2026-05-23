from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


class OTPRequiredMixin(LoginRequiredMixin):
    """
    Mixin untuk memastikan user sudah login DAN sudah verifikasi OTP.
    Digunakan di semua view yang butuh akses penuh.

    Flow:
    1. Belum login → redirect ke halaman login
    2. Sudah login tapi belum OTP verified → redirect ke halaman OTP
    3. Sudah login + OTP verified → lanjut
    """

    def dispatch(self, request, *args, **kwargs):
        # Cek login dulu via LoginRequiredMixin
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Cek apakah sudah OTP verified di session
        if not request.session.get('otp_verified', False):
            messages.warning(request, 'Silakan verifikasi OTP terlebih dahulu.')
            return redirect('authentication:otp_verify')

        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(OTPRequiredMixin):
    """
    Mixin khusus Admin.
    Hanya user dengan role='admin' yang boleh akses.
    Cek role SEBELUM memanggil super() untuk mencegah processing request.
    """

    def dispatch(self, request, *args, **kwargs):
        # Cek login + OTP dulu via OTPRequiredMixin
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.session.get('otp_verified', False):
            messages.warning(request, 'Silakan verifikasi OTP terlebih dahulu.')
            return redirect('authentication:otp_verify')

        # Cek role SEBELUM super() (penting! agar POST tidak diproses untuk non-admin)
        if not request.user.is_admin_role:
            messages.error(request, 'Akses ditolak. Halaman ini hanya untuk Admin.')
            raise PermissionDenied

        # Role OK → lanjut ke view
        from django.views import View
        return View.dispatch(self, request, *args, **kwargs)


class HRDRequiredMixin(OTPRequiredMixin):
    """Mixin untuk HRD dan Admin. Cek role sebelum processing."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.session.get('otp_verified', False):
            messages.warning(request, 'Silakan verifikasi OTP terlebih dahulu.')
            return redirect('authentication:otp_verify')

        if not (request.user.is_admin_role or request.user.is_hrd_role):
            messages.error(request, 'Akses ditolak. Halaman ini hanya untuk HRD atau Admin.')
            raise PermissionDenied

        from django.views import View
        return View.dispatch(self, request, *args, **kwargs)


class RoleBasedDashboardMixin(OTPRequiredMixin):
    """
    Mixin umum untuk dashboard.
    Cukup pastikan sudah login dan OTP verified.
    """
    pass
