import io
import base64

import qrcode
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, TemplateView
)

from .forms import LoginForm, OTPVerifyForm, UserCreateForm, UserUpdateForm
from .mixins import OTPRequiredMixin, AdminRequiredMixin, RoleBasedDashboardMixin
from .models import CustomUser


# ═══════════════════════════════════════════════════════
# AUTHENTICATION VIEWS
# ═══════════════════════════════════════════════════════

class CustomLoginView(LoginView):
    """
    Login View menggunakan Django built-in LoginView.
    Setelah credentials benar → redirect ke OTP verify.
    """
    form_class = LoginForm
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        """
        Override: jangan langsung login penuh.
        Simpan user_id di session sementara, redirect ke OTP.
        """
        user = form.get_user()

        # Simpan user_id di session (pre-auth, belum full login)
        self.request.session['pre_auth_user_id'] = user.pk
        self.request.session['otp_verified'] = False

        # Generate OTP secret jika belum ada
        if not user.otp_secret:
            user.generate_otp_secret()

        # Kalau OTP belum pernah di-setup, arahkan ke setup dulu
        if not user.is_otp_enabled:
            return redirect('authentication:otp_setup')

        return redirect('authentication:otp_verify')

    def get_success_url(self):
        return reverse('authentication:otp_verify')


class OTPSetupView(View):
    """
    Halaman setup OTP pertama kali.
    Tampilkan QR Code untuk di-scan Google Authenticator.
    """
    template_name = 'authentication/otp_setup.html'

    def _get_pre_auth_user(self):
        """Ambil user dari session pre-auth."""
        user_id = self.request.session.get('pre_auth_user_id')
        if not user_id:
            return None
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None

    def _generate_qr_code_base64(self, uri: str) -> str:
        """Generate QR code dan kembalikan sebagai base64 string."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def get(self, request):
        user = self._get_pre_auth_user()
        if not user:
            messages.error(request, 'Sesi tidak valid. Silakan login ulang.')
            return redirect('authentication:login')

        # Pastikan secret sudah ada
        if not user.otp_secret:
            user.generate_otp_secret()

        uri = user.get_totp_uri()
        qr_code_b64 = self._generate_qr_code_base64(uri)

        return self._render(request, user, qr_code_b64)

    def post(self, request):
        user = self._get_pre_auth_user()
        if not user:
            messages.error(request, 'Sesi tidak valid. Silakan login ulang.')
            return redirect('authentication:login')

        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            if user.verify_otp(token):
                # Tandai OTP sudah di-enable
                user.is_otp_enabled = True
                user.save(update_fields=['is_otp_enabled'])

                # Full login
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                request.session['otp_verified'] = True
                del request.session['pre_auth_user_id']

                messages.success(request, f'Selamat datang, {user.get_full_name() or user.username}! OTP berhasil dikonfigurasi.')
                return redirect(reverse(user.get_dashboard_url()))
            else:
                messages.error(request, 'Kode OTP salah. Pastikan waktu HP dan PC sudah sinkron.')

        uri = user.get_totp_uri()
        qr_code_b64 = self._generate_qr_code_base64(uri)
        return self._render(request, user, qr_code_b64, form=form)

    def _render(self, request, user, qr_code_b64, form=None):
        from django.shortcuts import render
        if form is None:
            form = OTPVerifyForm()
        return render(request, self.template_name, {
            'user_obj': user,
            'qr_code_b64': qr_code_b64,
            'otp_secret': user.otp_secret,
            'form': form,
        })


class OTPVerifyView(View):
    """
    Halaman verifikasi OTP setelah login credentials benar.
    User memasukkan 6 digit dari Google Authenticator.
    """
    template_name = 'authentication/otp_verify.html'

    def _get_pre_auth_user(self):
        user_id = self.request.session.get('pre_auth_user_id')
        if not user_id:
            return None
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None

    def get(self, request):
        # Kalau sudah full verified, langsung ke dashboard
        if request.user.is_authenticated and request.session.get('otp_verified'):
            return redirect(reverse(request.user.get_dashboard_url()))

        user = self._get_pre_auth_user()
        if not user:
            messages.error(request, 'Sesi tidak valid. Silakan login ulang.')
            return redirect('authentication:login')

        form = OTPVerifyForm()
        return self._render(request, user, form)

    def post(self, request):
        user = self._get_pre_auth_user()
        if not user:
            messages.error(request, 'Sesi tidak valid. Silakan login ulang.')
            return redirect('authentication:login')

        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            if user.verify_otp(token):
                # Full login
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                request.session['otp_verified'] = True
                # Hapus pre-auth session
                if 'pre_auth_user_id' in request.session:
                    del request.session['pre_auth_user_id']

                messages.success(request, f'Selamat datang kembali, {user.get_full_name() or user.username}!')
                return redirect(reverse(user.get_dashboard_url()))
            else:
                messages.error(request, 'Kode OTP salah atau sudah expired. Coba lagi.')

        return self._render(request, user, form)

    def _render(self, request, user, form):
        from django.shortcuts import render
        return render(request, self.template_name, {
            'form': form,
            'user_obj': user,
        })


class CustomLogoutView(View):
    """Logout + bersihkan session OTP."""

    def post(self, request):
        # Bersihkan session OTP
        request.session.pop('otp_verified', None)
        request.session.pop('pre_auth_user_id', None)
        logout(request)
        messages.info(request, 'Anda telah berhasil logout.')
        return redirect('authentication:login')

    def get(self, request):
        # Untuk keamanan, logout juga bisa via GET (fallback)
        request.session.pop('otp_verified', None)
        request.session.pop('pre_auth_user_id', None)
        logout(request)
        return redirect('authentication:login')


# ═══════════════════════════════════════════════════════
# DASHBOARD VIEWS
# ═══════════════════════════════════════════════════════

class DashboardRedirectView(OTPRequiredMixin, View):
    """
    View utama / yang redirect ke dashboard sesuai role.
    """
    def get(self, request):
        return redirect(reverse(request.user.get_dashboard_url()))


class DashboardAdminView(AdminRequiredMixin, TemplateView):
    """Dashboard khusus Admin."""
    template_name = 'authentication/dashboard_admin.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_users'] = CustomUser.objects.count()
        ctx['total_admin'] = CustomUser.objects.filter(role=CustomUser.Role.ADMIN).count()
        ctx['total_hrd'] = CustomUser.objects.filter(role=CustomUser.Role.HRD).count()
        ctx['total_staff'] = CustomUser.objects.filter(role=CustomUser.Role.STAFF).count()
        ctx['recent_users'] = CustomUser.objects.order_by('-date_joined')[:5]
        return ctx


class DashboardHRDView(RoleBasedDashboardMixin, TemplateView):
    """Dashboard khusus HRD."""
    template_name = 'authentication/dashboard_hrd.html'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if hasattr(response, 'status_code') and response.status_code in (301, 302):
            return response
        # HRD dan Admin boleh akses
        if not (request.user.is_hrd_role or request.user.is_admin_role):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return response


class DashboardStaffView(OTPRequiredMixin, TemplateView):
    """Dashboard khusus Staff."""
    template_name = 'authentication/dashboard_staff.html'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if hasattr(response, 'status_code') and response.status_code in (301, 302):
            return response
        if not (request.user.is_staff_role or request.user.is_admin_role):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return response


# ═══════════════════════════════════════════════════════
# USER MANAGEMENT (Admin Only) — CRUD CBV
# ═══════════════════════════════════════════════════════

class UserListView(AdminRequiredMixin, ListView):
    """Daftar semua pengguna. Hanya Admin."""
    model = CustomUser
    template_name = 'authentication/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        qs = CustomUser.objects.all().order_by('-date_joined')
        # Filter pencarian
        search = self.request.GET.get('search', '').strip()
        role_filter = self.request.GET.get('role', '').strip()
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        if role_filter:
            qs = qs.filter(role=role_filter)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('search', '')
        ctx['role_filter'] = self.request.GET.get('role', '')
        ctx['role_choices'] = CustomUser.Role.choices
        return ctx


class UserCreateView(AdminRequiredMixin, CreateView):
    """Tambah pengguna baru. Hanya Admin."""
    model = CustomUser
    form_class = UserCreateForm
    template_name = 'authentication/user_form.html'
    success_url = reverse_lazy('authentication:user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Generate OTP secret otomatis saat user baru dibuat
        self.object.generate_otp_secret()
        messages.success(
            self.request,
            f'Pengguna "{self.object.username}" berhasil ditambahkan.'
        )
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Terdapat kesalahan pada form. Periksa kembali data yang diisi.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_title'] = 'Tambah Pengguna Baru'
        ctx['btn_label'] = 'Simpan Pengguna'
        ctx['is_create'] = True
        return ctx


class UserUpdateView(AdminRequiredMixin, UpdateView):
    """Edit pengguna. Hanya Admin."""
    model = CustomUser
    form_class = UserUpdateForm
    template_name = 'authentication/user_form.html'
    success_url = reverse_lazy('authentication:user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Data pengguna "{self.object.username}" berhasil diperbarui.'
        )
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Terdapat kesalahan pada form. Periksa kembali data yang diisi.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_title'] = f'Edit Pengguna: {self.object.username}'
        ctx['btn_label'] = 'Perbarui Data'
        ctx['is_create'] = False
        return ctx


class UserDeleteView(AdminRequiredMixin, DeleteView):
    """Hapus pengguna. Hanya Admin. Tidak bisa hapus diri sendiri."""
    model = CustomUser
    template_name = 'authentication/user_confirm_delete.html'
    success_url = reverse_lazy('authentication:user_list')

    def dispatch(self, request, *args, **kwargs):
        # Cek self-delete sebelum super() (yang akan cek AdminRequired)
        if request.user.is_authenticated:
            target_pk = kwargs.get('pk')
            if target_pk and str(request.user.pk) == str(target_pk):
                messages.error(request, 'Anda tidak dapat menghapus akun Anda sendiri.')
                return redirect('authentication:user_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        username = self.object.username
        response = super().form_valid(form)
        messages.success(self.request, f'Pengguna "{username}" berhasil dihapus.')
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user_obj'] = self.object
        return ctx


class UserResetOTPView(AdminRequiredMixin, View):
    """Reset OTP secret user. Hanya Admin."""

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.otp_secret = None
        user.is_otp_enabled = False
        user.save(update_fields=['otp_secret', 'is_otp_enabled'])
        messages.success(request, f'OTP untuk pengguna "{user.username}" berhasil direset. Pengguna harus setup OTP ulang saat login berikutnya.')
        return redirect('authentication:user_list')


# ═══════════════════════════════════════════════════════
# PROFILE & CHANGE PASSWORD
# ═══════════════════════════════════════════════════════

class ProfileView(OTPRequiredMixin, TemplateView):
    """Halaman profil milik user yang sedang login."""
    template_name = 'authentication/profile.html'


class ChangePasswordView(OTPRequiredMixin, View):
    """
    Ubah password sendiri.
    Gunakan update_session_auth_hash agar session tidak expired setelah ganti password.
    """

    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            # Pastikan OTP verified tidak hilang dari session setelah password diganti
            request.session['otp_verified'] = True
            messages.success(request, 'Password berhasil diubah. Silakan login ulang jika diminta.')
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
        return redirect('authentication:profile')

    def get(self, request):
        return redirect('authentication:profile')
