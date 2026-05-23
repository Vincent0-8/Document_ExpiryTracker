import pyotp
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom User Model dengan role dan OTP support.
    Extends AbstractUser agar tetap compatible dengan Django auth system.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        HRD = 'hrd', 'HRD'
        STAFF = 'staff', 'Staff/Karyawan'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STAFF,
        verbose_name='Role Pengguna'
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Nomor HP'
    )
    is_otp_enabled = models.BooleanField(
        default=False,
        verbose_name='OTP Aktif'
    )
    otp_secret = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name='OTP Secret Key'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pengguna'
        verbose_name_plural = 'Pengguna'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    # ─── OOP: Enkapsulasi OTP logic di dalam model ───

    def generate_otp_secret(self):
        """Generate secret key baru untuk OTP."""
        self.otp_secret = pyotp.random_base32()
        self.save(update_fields=['otp_secret'])
        return self.otp_secret

    def get_totp_uri(self):
        """Kembalikan URI untuk QR Code Google Authenticator."""
        if not self.otp_secret:
            self.generate_otp_secret()
        totp = pyotp.TOTP(self.otp_secret)
        return totp.provisioning_uri(
            name=self.email or self.username,
            issuer_name='DocuGuard ERP'
        )

    def verify_otp(self, token: str) -> bool:
        """
        Verifikasi token OTP dari Google Authenticator.
        valid_window=1 toleransi ±30 detik clock skew.
        """
        if not self.otp_secret:
            return False
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(token, valid_window=1)

    # ─── Role helper properties ───

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_hrd_role(self):
        return self.role == self.Role.HRD

    @property
    def is_staff_role(self):
        return self.role == self.Role.STAFF

    def get_dashboard_url(self):
        """Redirect URL berdasarkan role."""
        dashboard_map = {
            self.Role.ADMIN: 'authentication:dashboard_admin',
            self.Role.HRD: 'authentication:dashboard_hrd',
            self.Role.STAFF: 'authentication:dashboard_staff',
        }
        return dashboard_map.get(self.role, 'authentication:dashboard_staff')
