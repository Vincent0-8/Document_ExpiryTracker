# 📋 Step-by-Step Pengerjaan Jobdesk Vincent

## Design System Yang Akan Dipakai (HARUS SAMA PERSIS)
> Wajib konsisten dengan template teman-teman agar tidak kelihatan berbeda gaya.

- **CSS Framework**: Bootstrap 5.3.3 (CDN)
- **Icons**: Tabler Icons 2.44.0 (CDN)
- **Font**: Plus Jakarta Sans + DM Mono (Google Fonts)
- **Warna**: Menggunakan CSS variables yang sama persis:
  - `--blue: #2563eb` (primary actions)
  - `--green: #16a34a` (aktif/sukses)
  - `--red: #dc2626` (expired/hapus)
  - `--amber: #d97706` (peringatan)
  - `--bg-base: #f4f5f7` (background halaman)
  - `--bg-card: #fff` (background card)

---

## 📌 FASE 1: Backend (Views & URLs)

### Step 1 — Update `views.py`
**File:** `core/views.py`

Tambahkan 2 view baru:

1. **`dashboard_staff`** (sudah ada tapi kosong) — diupdate menjadi dinamis:
   - Kirim data statistik dokumen milik user yang login ke template
   - Hitung: total dokumen, dokumen aktif, expired, dan hampir expired (dalam 14 hari)
   - Ambil daftar dokumen yang hampir expired untuk ditampilkan sebagai notifikasi

2. **`DokumenStaffListView`** (baru, pakai `ListView`):
   - Jika user = Staff → hanya tampilkan dokumen miliknya sendiri (`pemilik=request.user.pegawai`)
   - Jika user = Admin → tampilkan SEMUA dokumen staff
   - Support filter berdasarkan `jenis_dokumen`
   - Support pencarian berdasarkan `judul_dokumen`

3. **`DokumenStaffDetailView`** (baru, pakai `DetailView`):
   - Validasi keamanan: staff lain tidak boleh mengakses dokumen orang lain lewat URL
   - Tampilkan detail lengkap + perhitungan sisa hari pakai `hitung_sisa_hari()`

---

### Step 2 — Update `urls.py`
**File:** `core/urls.py`

Tambahkan 2 URL baru (menggantikan placeholder):
```python
path('doc_staff/',         DokumenStaffListView.as_view(),   name='doc_staff'),
path('doc_staff/<int:pk>/', DokumenStaffDetailView.as_view(), name='doc_staff_detail'),
```

---

## 📌 FASE 2: Frontend (Templates HTML)

Semua template menggunakan style yang SAMA PERSIS dengan `dashboard_utama.html` (sidebar, topbar, card, warna, font).

### Step 3 — Update `dashboard_staff.html`
**File:** `core/templates/core/dashboard_staff.html`

Halaman ini adalah **Dashboard khusus Staff/Karyawan**. Konten:
- Welcome banner (nama user yang login)
- 4 stat card: Total Dokumen, Aktif, Expired, Hampir Expired
- Tabel notifikasi: dokumen yang akan expired dalam 14 hari
- Tombol akses cepat ke "Daftar Dokumen Saya"

---

### Step 4 — Buat `dokumen_staff_list.html` (BARU)
**File:** `core/templates/core/dokumen_staff_list.html`

Halaman **Daftar Dokumen Staff**. Konten:
- Search bar + dropdown filter jenis dokumen (KTP, SIM, Paspor, dll)
- Tabel responsif: No. Referensi, Judul, Jenis, Berlaku s/d, Sisa Hari, Status, Aksi
- Badge status berwarna: Hijau (Aktif), Oranye (< 14 hari), Merah (Expired)
- Tombol "Detail" untuk setiap baris

---

### Step 5 — Buat `dokumen_staff_detail.html` (BARU)
**File:** `core/templates/core/dokumen_staff_detail.html`

Halaman **Detail Dokumen Staff**. Konten:
- Kartu info lengkap: Nomor Referensi, Judul, Jenis, Kategori, Pemilik
- Progress bar / countdown sisa hari masa berlaku
- Tombol download file lampiran
- Tombol kembali ke daftar

---

## 📌 FASE 3: Data Dummy (Opsional, untuk Pengujian)

### Step 6 — Buat Management Command `seed_dummy_data.py` (BARU)
**File:** `core/management/commands/seed_dummy_data.py`

Command yang dijalankan dengan:
```bash
python manage.py seed_dummy_data
```

Akan membuat data dummy:
- Kategori dokumen (KTP, SIM, Paspor, dll)
- Dokumen Staff dengan variasi status (Aktif, Hampir Expired, Expired)
- Semua dokumen dimiliki oleh user `vincent`

---

## 📌 FASE 4: Pengujian (Wajib Dilakukan Sebelum Push)

### Step 7 — Pengujian Manual

Lakukan uji akses berikut di browser setelah semua kode selesai:

| Pengujian | URL | Hasil yang Diharapkan |
|---|---|---|
| Dashboard Staff | `/dashboard_staff/` | Muncul stat card dan notifikasi dokumen |
| Daftar Dokumen | `/doc_staff/` | Hanya muncul dokumen milik vincent |
| Detail Dokumen | `/doc_staff/1/` | Muncul detail + sisa hari |
| Keamanan URL | `/doc_staff/<id_orang_lain>/` | Redirect, tidak bisa diakses |

---

## 📌 FASE 5: Push ke GitHub

### Step 8 — Commit & Push ke Branch vincent

Setelah semua selesai dan sudah diuji di browser:

```bash
git status
git add .
git commit -m "feat: selesai fitur Dokumen Staff - dashboard, list, detail - Vincent"
git push origin vincent
```

Setelah push berhasil, **beritahu Arsat atau Damai** untuk melakukan Merge/Pull Request di GitHub dari branch `vincent` ke branch `main`.

---

## ✅ Ringkasan Urutan Eksekusi

```
Step 1 → Update views.py (backend logic)
Step 2 → Update urls.py (routing)
Step 3 → Update dashboard_staff.html (template dinamis)
Step 4 → Buat dokumen_staff_list.html (template baru)
Step 5 → Buat dokumen_staff_detail.html (template baru)
Step 6 → Buat seed_dummy_data.py (data uji, opsional)
Step 7 → Uji semua halaman di browser
Step 8 → Git add, commit, push ke GitHub
```
