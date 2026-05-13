import pyotp
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Pegawai(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nama_lengkap = models.CharField(max_length=100)
    jabatan = models.CharField(max_length=50)
    nomor_lengkap = models.CharField(max_length=15)
    kunci_otp = models.CharField(max_length=32, default=pyotp.random_base32)
    grup_pengguna = models.CharField(max_length=20)

class Kategori(models.Model):
    kode_kategori = models.CharField(max_length=10, unique=True)
    nama_kategori = models.CharField(max_length=50)
    level_urgensi = models.CharField(max_length=20)
    deskripsi = models.TextField()
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)

class DokumenDasar(models.Model):
    nomor_referensi = models.CharField(max_length=20, unique=True)
    judul_dokumen = models.CharField(max_length=100)
    file_lampiran = models.FileField(upload_to='dokumen/')
    tanggal_berlaku = models.DateField()
    tanggal_kedaluwarsa = models.DateField()
    pembuat = models.ForeignKey(Pegawai, on_delete=models.CASCADE)
    status_dokumen = models.CharField(max_length=20, default='Aktif')

    class Meta:
        abstract = True

    #ENKAPSULASI
    def perbarui_status(self, status_baru):
        self.status_dokumen = status_baru
        self.save()

    #POLIMORFISME
    def hitung_sisa_hari(self):
        selisih = self.tanggal_kedaluwarsa - timezone.now().date()
        return selisih.days
    
class DokumenHRD(DokumenDasar):
    departemen = models.CharField(max_length=50, default='HRD')

    #POLIMORFISME
    def hitung_sisa_hari(self):
        selisih = self.tanggal_kedaluwarsa - timezone.now().date()
        return selisih.days - 7
    
class DokumenFinance(DokumenDasar):
    departemen = models.CharField(max_length=50, default='Finance')

    #POLIMORFISME
    def hitung_sisa_hari(self):
        selisih = self.tanggal_kedaluwarsa - timezone.now().date()
        return selisih.days - 14

class LogAktivitas(models.Model):
    id_catatan = models.AutoField(primary_key=True)
    referensi_dokumen = models.CharField(max_length=20)
    nama_pegawai = models.CharField(max_length=100)
    jenis_aksi = models.CharField(max_length=50)
    waktu_catatan = models.DateTimeField(auto_now_add=True)