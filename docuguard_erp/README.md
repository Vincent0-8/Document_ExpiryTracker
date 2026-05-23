# DocuGuard ERP — Modul Autentikasi (Julianto)

Sistem autentikasi lengkap dengan OTP Google Authenticator, Role-Based Access Control, dan User Management untuk project kelompok DocuGuard ERP.

---

## Fitur Lengkap

- Login dengan username & password
- Verifikasi OTP Google Authenticator (6 digit TOTP)
- Setup OTP pertama kali dengan QR Code
- Dashboard berbeda untuk Admin, HRD, dan Staff
- CRUD User Management (hanya Admin)
- Middleware OTP global (semua route otomatis terlindungi)
- Change password
- Halaman profil
- Session management
- Role-based access control

---

## Setup Awal

### 1. Clone repo dan masuk branch

```bash
git clone https://github.com/pandaa-tt/docuguard_erp.git
cd docuguard_erp
git checkout -b julianto
```

### 2. Buat virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Jalankan migrasi

```bash
python manage.py makemigrations authentication
python manage.py migrate
```

### 5. Buat data dummy (opsional, untuk testing)

```bash
python manage.py create_dummy_users
```

### 6. Jalankan server

```bash
python manage.py runserver
```

Buka browser: **http://127.0.0.1:8000/**

---

## Akun Default

Setelah `create_dummy_users`:

| Username     | Password     | Role  |
|-------------|-------------|-------|
| admin_utama | Admin@12345 | Admin |
| julianto    | Julianto123 | Admin |
| jacky       | Jacky12345  | HRD   |
| vincent     | Vincent123  | Staff |
| karyawan1   | Kar@12345   | Staff |

> **Catatan:** Semua akun perlu setup OTP saat pertama kali login.

---

## Alur Login

```
1. Buka /auth/login/
2. Masukkan username & password
3. Pertama kali → scan QR Code dengan Google Authenticator
4. Berikutnya → masukkan kode 6 digit dari Google Authenticator
5. Redirect otomatis ke dashboard sesuai role
```

---

## URL Lengkap

| URL | Keterangan |
|-----|-----------|
| `/auth/login/` | Halaman login |
| `/auth/logout/` | Logout |
| `/auth/otp/setup/` | Setup OTP pertama kali |
| `/auth/otp/verify/` | Verifikasi OTP |
| `/auth/dashboard/` | Redirect ke dashboard sesuai role |
| `/auth/dashboard/admin/` | Dashboard Admin |
| `/auth/dashboard/hrd/` | Dashboard HRD |
| `/auth/dashboard/staff/` | Dashboard Staff |
| `/auth/profile/` | Halaman profil |
| `/auth/profile/change-password/` | Ganti password |
| `/auth/users/` | Daftar pengguna (Admin only) |
| `/auth/users/create/` | Tambah pengguna (Admin only) |
| `/auth/users/<pk>/edit/` | Edit pengguna (Admin only) |
| `/auth/users/<pk>/delete/` | Hapus pengguna (Admin only) |
| `/auth/users/<pk>/reset-otp/` | Reset OTP user (Admin only) |

---

## Jalankan Tests

```bash
# Semua test
python manage.py test authentication -v 2

# Test spesifik
python manage.py test authentication.tests.LoginViewTest -v 2
python manage.py test authentication.tests.OTPVerifyViewTest -v 2
python manage.py test authentication.tests.UserManagementTest -v 2
python manage.py test authentication.tests.OTPMiddlewareTest -v 2
```

---

## Struktur File

```
authentication/
├── models.py           ← CustomUser dengan OTP dan role
├── forms.py            ← LoginForm, OTPVerifyForm, UserCreateForm, UserUpdateForm
├── views.py            ← Semua CBV (Login, OTP, Dashboard, CRUD, Profile)
├── urls.py             ← Semua routing
├── mixins.py           ← OTPRequiredMixin, AdminRequiredMixin, HRDRequiredMixin
├── middleware.py       ← OTPMiddleware (proteksi global)
├── context_processors.py ← Inject role info ke semua template
├── admin.py            ← CustomUserAdmin
├── tests.py            ← 40+ unit & integration tests
├── management/
│   └── commands/
│       └── create_dummy_users.py
└── templates/
    └── authentication/
        ├── base.html              ← Layout utama (sidebar + topbar)
        ├── login.html
        ├── otp_setup.html
        ├── otp_verify.html
        ├── dashboard_admin.html
        ├── dashboard_hrd.html
        ├── dashboard_staff.html
        ├── profile.html
        ├── user_list.html
        ├── user_form.html
        └── user_confirm_delete.html
```

---

## Deploy ke PythonAnywhere (Damai)

```bash
# 1. Upload project ke PythonAnywhere
# 2. Di console PythonAnywhere:
pip install -r requirements.txt

# 3. Di settings.py ubah:
DEBUG = False
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Migrate
python manage.py migrate

# 6. Reload web app
```

---

## Git Workflow

```bash
# Setelah selesai coding
git status
git add .
git commit -m "feat: authentication module lengkap - Login, OTP, RBAC, CRUD User - Julianto"
git push origin julianto

# Lalu buat Pull Request di GitHub
# Merge dilakukan oleh Arsat atau Damai
```

---

## Cara Anggota Lain Integrasi

Lihat file **PANDUAN_INTEGRASI.txt** untuk panduan lengkap cara Jacky, Vincent, Damai, dan Arsat menggunakan sistem auth ini.

Singkatnya:
```python
# Di views.py app masing-masing
from authentication.mixins import OTPRequiredMixin, HRDRequiredMixin, AdminRequiredMixin

class MyView(HRDRequiredMixin, ListView):
    ...
```

```html
<!-- Di template masing-masing -->
{% extends 'authentication/base.html' %}
{% block content %}
  <!-- konten kalian -->
{% endblock %}
```
