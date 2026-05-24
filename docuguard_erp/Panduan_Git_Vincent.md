# 🚀 Panduan Git & Cara Memulai - Vincent

Dokumen ini adalah panduan langkah demi langkah bagi Anda (**Vincent**) untuk memahami kondisi Git saat ini, cara memverifikasinya sendiri di terminal VS Code, serta langkah-langkah menjalankan server Django sebelum mulai menulis kode.

---

## 🔍 Bagian 1: Memverifikasi Kondisi Saat Ini (Lakukan Sendiri di VS Code)

Semua perintah Git sinkronisasi sebelumnya **sudah berhasil saya jalankan secara langsung di komputer Anda** (karena saya memiliki akses terminal terintegrasi).

Untuk membuktikannya dan membuat Anda 100% yakin, silakan **buka Terminal di VS Code Anda** (klik menu `Terminal` -> `New Terminal`) dan jalankan dua perintah berikut:

### 1. Cek Branch Aktif Anda
Ketik perintah ini di terminal:
```bash
git branch
```
*   **Hasil yang harusnya muncul:**
    ```bash
    * vincent
      main
    ```
    *(Tanda bintang `*` dan warna hijau pada nama `vincent` membuktikan Anda sudah berada di branch baru yang aman).*

### 2. Cek Status Perubahan
Ketik perintah ini di terminal:
```bash
git status
```
*   **Hasil yang harusnya muncul:**
    ```bash
    On branch vincent
    Your branch is up to date with 'origin/main'.
    nothing to commit, working tree clean
    ```
    *(Ini membuktikan folder kerja Anda sudah sangat bersih dan tidak ada file sampah dari virtual environment `venv` yang mengganggu).*

---

## 💻 Bagian 2: Cara Mengaktifkan Venv & Menjalankan Server Django

Sebelum Anda mulai menulis kode, pastikan Anda bisa menjalankan server lokal Django untuk melihat aplikasinya di browser.

### Langkah-Langkah Menjalankan Server:

1.  **Buka Terminal VS Code** Anda.
2.  Pastikan Anda berada di folder proyek Django (di dalam folder `docuguard_erp`). Jika belum, ketik:
    ```bash
    cd d:\Data Sekolah\Kuliah\Django\tugas_kelompok\docuguard_erp
    ```
3.  **Aktifkan Virtual Environment (venv)** Anda dengan mengetik perintah ini:
    *   *Untuk PowerShell (Default VS Code di Windows):*
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```
    *   *Untuk Command Prompt (CMD) biasa:*
        ```cmd
        .\venv\Scripts\activate.bat
        ```
    *(Jika berhasil aktif, akan muncul tanda `(venv)` di sebelah kiri baris input terminal Anda).*

4.  **Jalankan Server Django** dengan perintah:
    ```bash
    python manage.py runserver
    ```
5.  **Buka Browser** Anda dan akses alamat berikut untuk melihat aplikasinya:
    [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 💾 Bagian 3: Alur Kerja Git Selanjutnya (Setelah Selesai Coding)

Nanti kalau sudah beres review dan mau di-upload ke GitHub kelompok, tinggal jalankan ini di terminal VS Code:

```bash
git status
git add .
git commit -m "menyelesaikan fitur dokumen staff - Vincent"
git push origin vincent
```

Setelah push sukses, langsung kabari **Arsat** atau **Damai** buat merge dari branch `vincent` ke branch `main` di GitHub kelompok. Tidak perlu merge sendiri!
