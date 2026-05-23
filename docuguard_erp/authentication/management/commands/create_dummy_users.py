"""
authentication/management/commands/create_dummy_users.py

Jalankan dengan:
    python manage.py create_dummy_users

Membuat data dummy untuk testing semua role.
"""

from django.core.management.base import BaseCommand
from authentication.models import CustomUser


class Command(BaseCommand):
    help = 'Buat data dummy pengguna untuk semua role (testing)'

    def handle(self, *args, **options):
        dummy_users = [
            # (username, password, first_name, last_name, email, role)
            ('admin_utama', 'Admin@12345', 'Admin', 'Utama', 'admin@docuguard.com', 'admin'),
            ('julianto',    'Julianto123', 'Julianto', '', 'julianto@docuguard.com', 'admin'),
            ('jacky',       'Jacky12345',  'Jacky', 'Lian', 'jacky@docuguard.com', 'hrd'),
            ('vincent',     'Vincent123',  'Vincent', '', 'vincent@docuguard.com', 'staff'),
            ('damai',       'Damai12345',  'Damai', 'Alyndina', 'damai@docuguard.com', 'admin'),
            ('arsat',       'Arsat12345',  'Mohamed', 'Arsat', 'arsat@docuguard.com', 'admin'),
            ('hrd_staff1',  'Hrd@12345',   'Budi', 'Santoso', 'budi@docuguard.com', 'hrd'),
            ('karyawan1',   'Kar@12345',   'Siti', 'Rahayu', 'siti@docuguard.com', 'staff'),
            ('karyawan2',   'Kar@12345',   'Ahmad', 'Fauzi', 'ahmad@docuguard.com', 'staff'),
        ]

        created_count = 0
        skipped_count = 0

        for username, password, first_name, last_name, email, role in dummy_users:
            if CustomUser.objects.filter(username=username).exists():
                self.stdout.write(f'  ⏭  Skip: {username} (sudah ada)')
                skipped_count += 1
                continue

            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role,
                is_staff=(role == 'admin'),
                is_superuser=(username in ['admin_utama', 'julianto']),
            )
            # Generate OTP secret (tapi belum di-enable, user harus scan QR dulu)
            user.generate_otp_secret()

            self.stdout.write(
                self.style.SUCCESS(f'  ✓  Dibuat: {username} ({role}) — password: {password}')
            )
            created_count += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Selesai! {created_count} pengguna dibuat, {skipped_count} dilewati.'
        ))
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write('  Username: admin_utama | Password: Admin@12345 | Role: Admin')
        self.stdout.write('  Username: jacky       | Password: Jacky12345  | Role: HRD')
        self.stdout.write('  Username: karyawan1   | Password: Kar@12345   | Role: Staff')
