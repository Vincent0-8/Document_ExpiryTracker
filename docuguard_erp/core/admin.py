from django.contrib import admin
from .models import Pegawai, Kategori, DokumenHRD, DokumenStaff, LogAktivitas

@admin.register(Pegawai)
class PegawaiAdmin(admin.ModelAdmin):
    list_display  = ['nama_lengkap', 'jabatan', 'grup_pengguna', 'user']
    list_filter   = ['grup_pengguna']
    search_fields = ['nama_lengkap', 'jabatan']

@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display  = ['kode_kategori', 'nama_kategori', 'level_urgensi']
    list_filter   = ['level_urgensi']

@admin.register(DokumenHRD)
class DokumenHRDAdmin(admin.ModelAdmin):
    list_display  = ['nomor_referensi', 'judul_dokumen', 'jenis_dokumen',
                     'status_dokumen', 'tanggal_kedaluwarsa']
    list_filter   = ['status_dokumen', 'jenis_dokumen']
    search_fields = ['nomor_referensi', 'judul_dokumen']

@admin.register(DokumenStaff)
class DokumenStaffAdmin(admin.ModelAdmin):
    list_display  = ['nomor_referensi', 'judul_dokumen', 'jenis_dokumen',
                     'pemilik', 'status_dokumen', 'tanggal_kedaluwarsa']
    list_filter   = ['status_dokumen', 'jenis_dokumen']
    search_fields = ['nomor_referensi', 'judul_dokumen']

@admin.register(LogAktivitas)
class LogAktivitasAdmin(admin.ModelAdmin):
    list_display    = ['waktu_catatan', 'nama_pegawai', 'jenis_aksi', 'referensi_dokumen']
    list_filter     = ['jenis_aksi']
    search_fields   = ['nama_pegawai', 'referensi_dokumen']
    readonly_fields = ['waktu_catatan']