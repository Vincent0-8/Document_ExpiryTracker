"""
authentication/tests.py

Unit test + Integration test lengkap untuk semua fitur Julianto.
Jalankan dengan:
    python manage.py test authentication -v 2
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
import pyotp

from .models import CustomUser


# ─── Helper ───────────────────────────────────────────────

def make_user(username, role='staff', password='TestPass123!', otp_ready=True):
    """Buat user test dengan OTP secret."""
    user = CustomUser.objects.create_user(
        username=username,
        password=password,
        email=f'{username}@test.com',
        first_name=username.capitalize(),
        role=role,
    )
    if otp_ready:
        user.generate_otp_secret()
        user.is_otp_enabled = True
        user.save(update_fields=['is_otp_enabled'])
    return user


def get_valid_otp(user):
    """Generate OTP valid dari secret user."""
    return pyotp.TOTP(user.otp_secret).now()


# ═══════════════════════════════════════════════════════════
# 1. MODEL TESTS
# ═══════════════════════════════════════════════════════════

class CustomUserModelTest(TestCase):

    def setUp(self):
        self.user = make_user('testuser', role='staff')

    def test_user_str(self):
        """__str__ menampilkan nama dan role."""
        self.assertIn('Testuser', str(self.user))
        self.assertIn('Staff', str(self.user))

    def test_generate_otp_secret(self):
        """generate_otp_secret() menghasilkan string base32."""
        user = make_user('newuser', otp_ready=False)
        secret = user.generate_otp_secret()
        self.assertIsNotNone(secret)
        self.assertEqual(len(secret), 32)
        # Harus disimpan ke DB
        user.refresh_from_db()
        self.assertEqual(user.otp_secret, secret)

    def test_verify_otp_valid(self):
        """verify_otp() True untuk kode yang benar."""
        token = get_valid_otp(self.user)
        self.assertTrue(self.user.verify_otp(token))

    def test_verify_otp_invalid(self):
        """verify_otp() False untuk kode yang salah."""
        self.assertFalse(self.user.verify_otp('000000'))
        self.assertFalse(self.user.verify_otp('999999'))
        self.assertFalse(self.user.verify_otp('abcdef'))

    def test_verify_otp_no_secret(self):
        """verify_otp() False jika secret belum di-generate."""
        user = make_user('nosecret', otp_ready=False)
        self.assertFalse(user.verify_otp('123456'))

    def test_role_properties(self):
        """is_admin_role, is_hrd_role, is_staff_role benar."""
        admin = make_user('adm', role='admin')
        hrd = make_user('hrd1', role='hrd')
        staff = make_user('stf', role='staff')

        self.assertTrue(admin.is_admin_role)
        self.assertFalse(admin.is_hrd_role)
        self.assertFalse(admin.is_staff_role)

        self.assertTrue(hrd.is_hrd_role)
        self.assertFalse(hrd.is_admin_role)

        self.assertTrue(staff.is_staff_role)
        self.assertFalse(staff.is_admin_role)

    def test_get_dashboard_url(self):
        """get_dashboard_url() mengembalikan URL sesuai role."""
        admin = make_user('adm2', role='admin')
        hrd = make_user('hrd2', role='hrd')
        staff = make_user('stf2', role='staff')

        self.assertEqual(admin.get_dashboard_url(), 'authentication:dashboard_admin')
        self.assertEqual(hrd.get_dashboard_url(), 'authentication:dashboard_hrd')
        self.assertEqual(staff.get_dashboard_url(), 'authentication:dashboard_staff')

    def test_totp_uri_format(self):
        """get_totp_uri() menghasilkan URI dengan format benar."""
        uri = self.user.get_totp_uri()
        self.assertIn('otpauth://totp/', uri)
        self.assertIn('DocuGuard%20ERP', uri)
        self.assertIn(self.user.otp_secret, uri)


# ═══════════════════════════════════════════════════════════
# 2. LOGIN FLOW TESTS
# ═══════════════════════════════════════════════════════════

class LoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user('loginuser', role='staff')
        self.login_url = reverse('authentication:login')

    def test_login_page_loads(self):
        """Halaman login bisa diakses."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'DocuGuard')

    def test_login_wrong_credentials(self):
        """Login dengan password salah → tetap di halaman login."""
        response = self.client.post(self.login_url, {
            'username': 'loginuser',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        # Pastikan belum ada session pre_auth
        self.assertNotIn('pre_auth_user_id', self.client.session)

    def test_login_correct_credentials_redirects_to_otp(self):
        """Login benar → redirect ke halaman OTP verify."""
        response = self.client.post(self.login_url, {
            'username': 'loginuser',
            'password': 'TestPass123!',
        })
        self.assertRedirects(response, reverse('authentication:otp_verify'))
        # Session pre_auth harus terisi
        self.assertIn('pre_auth_user_id', self.client.session)
        self.assertEqual(self.client.session['pre_auth_user_id'], self.user.pk)

    def test_login_first_time_redirects_to_otp_setup(self):
        """User baru (OTP belum enable) → redirect ke otp_setup."""
        new_user = make_user('newbie', otp_ready=False)
        # Generate secret tapi belum enable
        new_user.generate_otp_secret()
        new_user.save()

        response = self.client.post(self.login_url, {
            'username': 'newbie',
            'password': 'TestPass123!',
        })
        self.assertRedirects(response, reverse('authentication:otp_setup'))

    def test_authenticated_redirected_user_goes_to_dashboard(self):
        """User yang sudah full login → redirect dari login ke dashboard."""
        # Simulasi full login dengan session
        self.client.force_login(self.user)
        session = self.client.session
        session['otp_verified'] = True
        session.save()

        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)


# ═══════════════════════════════════════════════════════════
# 3. OTP VERIFY TESTS
# ═══════════════════════════════════════════════════════════

class OTPVerifyViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user('otpuser', role='staff')
        self.otp_url = reverse('authentication:otp_verify')

        # Setup pre-auth session
        session = self.client.session
        session['pre_auth_user_id'] = self.user.pk
        session['otp_verified'] = False
        session.save()

    def test_otp_page_loads(self):
        """Halaman OTP verify bisa diakses dengan pre-auth session."""
        response = self.client.get(self.otp_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Verifikasi OTP')

    def test_otp_correct_code_full_login(self):
        """OTP benar → full login + redirect ke dashboard."""
        token = get_valid_otp(self.user)
        response = self.client.post(self.otp_url, {'token': token})

        # Harus redirect ke dashboard
        self.assertEqual(response.status_code, 302)
        # Session OTP verified harus True
        self.assertTrue(self.client.session.get('otp_verified', False))
        # pre_auth_user_id harus dihapus
        self.assertNotIn('pre_auth_user_id', self.client.session)

    def test_otp_wrong_code_stays_on_page(self):
        """OTP salah → tetap di halaman OTP dengan pesan error."""
        response = self.client.post(self.otp_url, {'token': '000000'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.get('otp_verified', False))

    def test_otp_non_numeric_rejected(self):
        """OTP huruf → form validation error."""
        response = self.client.post(self.otp_url, {'token': 'abcdef'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.get('otp_verified', False))

    def test_otp_less_than_6_digits_rejected(self):
        """OTP kurang dari 6 digit → ditolak."""
        response = self.client.post(self.otp_url, {'token': '123'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.get('otp_verified', False))

    def test_otp_verify_no_session_redirects_to_login(self):
        """Akses OTP verify tanpa pre-auth session → redirect ke login."""
        fresh_client = Client()
        response = fresh_client.get(self.otp_url)
        # Middleware redirect ke login
        self.assertEqual(response.status_code, 302)

    def test_otp_correct_redirects_by_role(self):
        """OTP benar → redirect sesuai role."""
        # Test staff
        token = get_valid_otp(self.user)
        response = self.client.post(self.otp_url, {'token': token})
        self.assertRedirects(response, reverse('authentication:dashboard_staff'))

    def test_admin_redirects_to_admin_dashboard(self):
        """Admin OTP benar → dashboard admin."""
        admin = make_user('admintest', role='admin')
        session = self.client.session
        session['pre_auth_user_id'] = admin.pk
        session['otp_verified'] = False
        session.save()

        token = get_valid_otp(admin)
        response = self.client.post(self.otp_url, {'token': token})
        self.assertRedirects(response, reverse('authentication:dashboard_admin'))

    def test_hrd_redirects_to_hrd_dashboard(self):
        """HRD OTP benar → dashboard HRD."""
        hrd = make_user('hrdtest', role='hrd')
        session = self.client.session
        session['pre_auth_user_id'] = hrd.pk
        session['otp_verified'] = False
        session.save()

        token = get_valid_otp(hrd)
        response = self.client.post(self.otp_url, {'token': token})
        self.assertRedirects(response, reverse('authentication:dashboard_hrd'))


# ═══════════════════════════════════════════════════════════
# 4. DASHBOARD ACCESS CONTROL TESTS
# ═══════════════════════════════════════════════════════════

class DashboardAccessTest(TestCase):

    def _login_as(self, role):
        """Helper: login penuh sebagai role tertentu."""
        user = make_user(f'user_{role}', role=role)
        self.client.force_login(user)
        session = self.client.session
        session['otp_verified'] = True
        session.save()
        return user

    def test_unauthenticated_blocked_from_dashboard(self):
        """User tidak login → tidak bisa akses dashboard."""
        response = self.client.get(reverse('authentication:dashboard_admin'))
        self.assertEqual(response.status_code, 302)

    def test_otp_not_verified_blocked(self):
        """User login tapi OTP belum verified → tidak bisa akses dashboard."""
        user = make_user('nonotp', role='admin')
        self.client.force_login(user)
        # session['otp_verified'] tidak di-set

        response = self.client.get(reverse('authentication:dashboard_admin'))
        self.assertEqual(response.status_code, 302)

    def test_admin_can_access_admin_dashboard(self):
        """Admin bisa akses dashboard admin."""
        self._login_as('admin')
        response = self.client.get(reverse('authentication:dashboard_admin'))
        self.assertEqual(response.status_code, 200)

    def test_hrd_cannot_access_admin_dashboard(self):
        """HRD tidak bisa akses dashboard admin."""
        self._login_as('hrd')
        response = self.client.get(reverse('authentication:dashboard_admin'))
        self.assertEqual(response.status_code, 403)

    def test_staff_cannot_access_admin_dashboard(self):
        """Staff tidak bisa akses dashboard admin."""
        self._login_as('staff')
        response = self.client.get(reverse('authentication:dashboard_admin'))
        self.assertEqual(response.status_code, 403)

    def test_hrd_can_access_hrd_dashboard(self):
        """HRD bisa akses dashboard HRD."""
        self._login_as('hrd')
        response = self.client.get(reverse('authentication:dashboard_hrd'))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_hrd_dashboard(self):
        """Admin juga bisa akses dashboard HRD."""
        self._login_as('admin')
        response = self.client.get(reverse('authentication:dashboard_hrd'))
        self.assertEqual(response.status_code, 200)

    def test_staff_cannot_access_hrd_dashboard(self):
        """Staff tidak bisa akses dashboard HRD."""
        self._login_as('staff')
        response = self.client.get(reverse('authentication:dashboard_hrd'))
        self.assertEqual(response.status_code, 403)

    def test_staff_can_access_staff_dashboard(self):
        """Staff bisa akses dashboard staff."""
        self._login_as('staff')
        response = self.client.get(reverse('authentication:dashboard_staff'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_redirect_based_on_role(self):
        """Dashboard redirect view → redirect ke URL sesuai role."""
        admin = self._login_as('admin')
        response = self.client.get(reverse('authentication:dashboard'))
        self.assertRedirects(response, reverse('authentication:dashboard_admin'))


# ═══════════════════════════════════════════════════════════
# 5. USER MANAGEMENT (CRUD) TESTS
# ═══════════════════════════════════════════════════════════

class UserManagementTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin = make_user('admin1', role='admin')
        self.hrd = make_user('hrd1', role='hrd')
        self.staff = make_user('staff1', role='staff')

    def _login_admin(self):
        self.client.force_login(self.admin)
        session = self.client.session
        session['otp_verified'] = True
        session.save()

    def _login_as(self, user):
        self.client.force_login(user)
        session = self.client.session
        session['otp_verified'] = True
        session.save()

    # ── List ──────────────────────────────────────────────

    def test_admin_can_view_user_list(self):
        """Admin bisa akses daftar pengguna."""
        self._login_admin()
        response = self.client.get(reverse('authentication:user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'admin1')

    def test_hrd_cannot_view_user_list(self):
        """HRD tidak bisa akses daftar pengguna."""
        self._login_as(self.hrd)
        response = self.client.get(reverse('authentication:user_list'))
        self.assertEqual(response.status_code, 403)

    def test_staff_cannot_view_user_list(self):
        """Staff tidak bisa akses daftar pengguna."""
        self._login_as(self.staff)
        response = self.client.get(reverse('authentication:user_list'))
        self.assertEqual(response.status_code, 403)

    def test_user_list_search(self):
        """Pencarian username di daftar pengguna."""
        self._login_admin()
        response = self.client.get(
            reverse('authentication:user_list'),
            {'search': 'hrd1'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'hrd1')
        self.assertNotContains(response, 'staff1')

    def test_user_list_filter_by_role(self):
        """Filter by role di daftar pengguna."""
        self._login_admin()
        response = self.client.get(
            reverse('authentication:user_list'),
            {'role': 'hrd'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'hrd1')

    # ── Create ────────────────────────────────────────────

    def test_admin_can_create_user(self):
        """Admin bisa membuat user baru."""
        self._login_admin()
        data = {
            'username': 'newstaff',
            'first_name': 'New',
            'last_name': 'Staff',
            'email': 'newstaff@test.com',
            'phone_number': '08123456789',
            'role': 'staff',
            'password1': 'StrongPass99!',
            'password2': 'StrongPass99!',
        }
        response = self.client.post(reverse('authentication:user_create'), data)
        self.assertRedirects(response, reverse('authentication:user_list'))
        self.assertTrue(CustomUser.objects.filter(username='newstaff').exists())

    def test_create_user_duplicate_email_fails(self):
        """Email duplikat → form error, user tidak dibuat."""
        self._login_admin()
        data = {
            'username': 'dupuser',
            'first_name': 'Dup',
            'last_name': '',
            'email': self.hrd.email,   # email sudah dipakai hrd1
            'role': 'staff',
            'password1': 'StrongPass99!',
            'password2': 'StrongPass99!',
        }
        response = self.client.post(reverse('authentication:user_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(username='dupuser').exists())

    def test_create_user_password_mismatch_fails(self):
        """Password tidak cocok → form error."""
        self._login_admin()
        data = {
            'username': 'mismatch',
            'first_name': 'X',
            'email': 'mismatch@test.com',
            'role': 'staff',
            'password1': 'StrongPass99!',
            'password2': 'DifferentPass!',
        }
        response = self.client.post(reverse('authentication:user_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(username='mismatch').exists())

    def test_hrd_cannot_create_user(self):
        """HRD tidak bisa akses halaman tambah user."""
        self._login_as(self.hrd)
        response = self.client.get(reverse('authentication:user_create'))
        self.assertEqual(response.status_code, 403)

    # ── Update ────────────────────────────────────────────

    def test_admin_can_update_user(self):
        """Admin bisa edit user."""
        self._login_admin()
        data = {
            'username': self.staff.username,
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com',
            'role': 'hrd',
            'is_active': True,
        }
        response = self.client.post(
            reverse('authentication:user_update', kwargs={'pk': self.staff.pk}),
            data
        )
        self.assertRedirects(response, reverse('authentication:user_list'))
        self.staff.refresh_from_db()
        self.assertEqual(self.staff.first_name, 'Updated')
        self.assertEqual(self.staff.role, 'hrd')

    def test_hrd_cannot_update_user(self):
        """HRD tidak bisa edit user."""
        self._login_as(self.hrd)
        response = self.client.get(
            reverse('authentication:user_update', kwargs={'pk': self.staff.pk})
        )
        self.assertEqual(response.status_code, 403)

    # ── Delete ────────────────────────────────────────────

    def test_admin_can_delete_user(self):
        """Admin bisa hapus user lain."""
        self._login_admin()
        target = make_user('tobedeleted')
        response = self.client.post(
            reverse('authentication:user_delete', kwargs={'pk': target.pk}),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(pk=target.pk).exists())

    def test_admin_cannot_delete_self(self):
        """Admin tidak bisa hapus akunnya sendiri."""
        self._login_admin()
        response = self.client.post(
            reverse('authentication:user_delete', kwargs={'pk': self.admin.pk}),
            follow=True
        )
        # Admin masih ada
        self.assertTrue(CustomUser.objects.filter(pk=self.admin.pk).exists())

    def test_hrd_cannot_delete_user(self):
        """HRD tidak bisa hapus user — ditolak oleh AdminRequiredMixin."""
        self._login_as(self.hrd)
        target = make_user('cannotdelete3')
        response = self.client.post(
            reverse('authentication:user_delete', kwargs={'pk': target.pk})
        )
        # Pastikan user target tidak terhapus — itu yang paling penting
        self.assertTrue(
            CustomUser.objects.filter(pk=target.pk).exists(),
            "Target user seharusnya tidak terhapus"
        )
        # Response bisa 403 (PermissionDenied) atau 302 (redirect ke login/otp)
        # tergantung session state, yang penting user tidak terhapus
        self.assertNotEqual(response.status_code, 200)

    # ── Reset OTP ─────────────────────────────────────────

    def test_admin_can_reset_user_otp(self):
        """Admin bisa reset OTP user lain."""
        self._login_admin()
        response = self.client.post(
            reverse('authentication:user_reset_otp', kwargs={'pk': self.hrd.pk})
        )
        self.assertRedirects(response, reverse('authentication:user_list'))
        self.hrd.refresh_from_db()
        self.assertFalse(self.hrd.is_otp_enabled)
        self.assertIsNone(self.hrd.otp_secret)


# ═══════════════════════════════════════════════════════════
# 6. LOGOUT TESTS
# ═══════════════════════════════════════════════════════════

class LogoutTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user('logoutuser', role='staff')

    def _full_login(self):
        self.client.force_login(self.user)
        session = self.client.session
        session['otp_verified'] = True
        session.save()

    def test_logout_clears_session(self):
        """Logout → session OTP verified dihapus."""
        self._full_login()
        self.client.post(reverse('authentication:logout'))
        self.assertFalse(self.client.session.get('otp_verified', False))
        self.assertFalse(self.client.session.get('pre_auth_user_id', False))

    def test_logout_redirects_to_login(self):
        """Logout → redirect ke halaman login."""
        self._full_login()
        response = self.client.post(reverse('authentication:logout'))
        self.assertRedirects(response, reverse('authentication:login'))

    def test_after_logout_dashboard_blocked(self):
        """Setelah logout → tidak bisa akses dashboard."""
        self._full_login()
        self.client.post(reverse('authentication:logout'))
        response = self.client.get(reverse('authentication:dashboard_staff'))
        self.assertEqual(response.status_code, 302)


# ═══════════════════════════════════════════════════════════
# 7. MIDDLEWARE TESTS
# ═══════════════════════════════════════════════════════════

class OTPMiddlewareTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user('midware_user', role='staff')

    def test_public_url_accessible_without_login(self):
        """Halaman login bisa diakses tanpa login."""
        response = self.client.get(reverse('authentication:login'))
        self.assertEqual(response.status_code, 200)

    def test_protected_url_blocked_without_login(self):
        """URL protected tidak bisa diakses tanpa login."""
        response = self.client.get(reverse('authentication:dashboard_staff'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response['Location'])

    def test_protected_url_blocked_without_otp(self):
        """Login tapi belum OTP → redirect ke halaman OTP (verify atau setup)."""
        self.client.force_login(self.user)
        # Tidak set session['otp_verified'] → middleware akan redirect
        response = self.client.get(reverse('authentication:dashboard_staff'))
        self.assertEqual(response.status_code, 302)
        location = response['Location']
        self.assertTrue(
            '/auth/otp/verify/' in location or '/auth/otp/setup/' in location,
            f"Expected redirect to OTP page, got: {location}"
        )

    def test_protected_url_accessible_after_full_login(self):
        """Sudah login + OTP verified → bisa akses protected URL."""
        self.client.force_login(self.user)
        session = self.client.session
        session['otp_verified'] = True
        session.save()
        response = self.client.get(reverse('authentication:dashboard_staff'))
        self.assertEqual(response.status_code, 200)


# ═══════════════════════════════════════════════════════════
# 8. PROFILE & CHANGE PASSWORD TESTS
# ═══════════════════════════════════════════════════════════

class ProfileTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user('profileuser', role='staff')
        self.client.force_login(self.user)
        session = self.client.session
        session['otp_verified'] = True
        session.save()

    def test_profile_page_loads(self):
        """Halaman profil bisa diakses."""
        response = self.client.get(reverse('authentication:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'profileuser')

    def test_change_password_success(self):
        """Ganti password dengan data benar → berhasil."""
        response = self.client.post(reverse('authentication:change_password'), {
            'old_password': 'TestPass123!',
            'new_password1': 'NewStrongPass99!',
            'new_password2': 'NewStrongPass99!',
        })
        self.assertRedirects(response, reverse('authentication:profile'))
        # Verify password benar-benar berubah
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrongPass99!'))

    def test_change_password_wrong_old(self):
        """Ganti password dengan old_password salah → gagal."""
        response = self.client.post(reverse('authentication:change_password'), {
            'old_password': 'WrongOldPass!',
            'new_password1': 'NewStrongPass99!',
            'new_password2': 'NewStrongPass99!',
        })
        self.assertRedirects(response, reverse('authentication:profile'))
        # Password tidak berubah
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('TestPass123!'))

    def test_change_password_keeps_session_active(self):
        """Setelah ganti password, sesi OTP tetap aktif (tidak logout)."""
        self.client.post(reverse('authentication:change_password'), {
            'old_password': 'TestPass123!',
            'new_password1': 'NewStrongPass99!',
            'new_password2': 'NewStrongPass99!',
        })
        self.assertTrue(self.client.session.get('otp_verified', False))
