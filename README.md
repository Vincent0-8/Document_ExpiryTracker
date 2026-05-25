# DocuGuard ERP — Fitur HRD (Jacky)

## Cara Menjalankan

```bash
# 1. Buat virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install django pyotp pillow

# 3. Migrate database
python manage.py migrate

# 4. Buat superuser
python manage.py createsuperuser

# 5. Buat Pengguna HRD via Django Admin (/admin/)
#    - Buat User, lalu buat Pengguna dengan role HRD atau Admin
#    - Buat minimal 1 Kategori di admin

# 6. Jalankan server
python manage.py runserver
```

## Halaman yang Tersedia

| URL | Nama | Keterangan |
|-----|------|------------|
| `/` | Dashboard HRD | Statistik + Reminder |
| `/dokumen/` | Daftar Dokumen | ListView + Filter + Paginasi |
| `/dokumen/tambah/` | Tambah Dokumen | CreateView + Upload File |
| `/dokumen/<pk>/` | Detail Dokumen | DetailView |
| `/dokumen/<pk>/edit/` | Edit Dokumen | UpdateView |
| `/dokumen/<pk>/hapus/` | Hapus Dokumen | DeleteView |
| `/accounts/login/` | Login | Auth HRD/Admin |

## Class-Based Views yang Digunakan

- `DashboardView` → TemplateView (extended HRDAdminMixin)
- `DokumenListView` → **ListView**
- `DokumenCreateView` → **CreateView**
- `DokumenUpdateView` → **UpdateView**
- `DokumenDetailView` → **DetailView**
- `DokumenDeleteView` → **DeleteView**

## Jenis Dokumen HRD

1. Kontrak Kerja
2. Sertifikat Pelatihan
3. BPJS Karyawan
4. Medical Check Up
5. Surat Peringatan

## Konsep Enkapsulasi

Status dokumen **hanya bisa diubah** melalui method `perbarui_status(status_baru)`.
Field `_status_dokumen` bersifat private dan tidak bisa diubah langsung dari database.

```python
# BENAR — via method enkapsulasi
dokumen.perbarui_status('Expired')

# Status diperbarui otomatis sesuai tanggal
dokumen.cek_dan_perbarui_status()
```

## Akses Control

Hanya user dengan `role_pengguna = 'HRD'` atau `'Admin'` yang dapat mengakses semua halaman dokumen HRD.
