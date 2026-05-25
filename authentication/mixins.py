from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


class OTPRequiredMixin(LoginRequiredMixin):
    """User harus sudah login DAN sudah verifikasi OTP."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.session.get('otp_verified'):
            return redirect('authentication:otp_verify')
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(OTPRequiredMixin, UserPassesTestMixin):
    """Hanya Admin yang boleh akses."""

    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.is_admin_role

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('authentication:login')
        return redirect('authentication:dashboard')


class RoleBasedDashboardMixin(OTPRequiredMixin):
    """Redirect ke dashboard sesuai role kalau akses halaman yang salah."""

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return redirect('authentication:login')
        return response