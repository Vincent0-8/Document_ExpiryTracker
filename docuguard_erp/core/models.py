import pyotp
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ─── ABSTRAKSI ───────────────────────────────────────────────────────────────
class DokumenDasar(models.Model):
    nomor_referensi     = models.CharField(max_length=20, unique=True)
    judul_dokumen       = models.CharField(max_length=100)
    file_lampiran       = models.FileField(upload_to='dokumen/')
    tanggal_berlaku     = models.DateField()
    tanggal_kedaluwarsa = models.DateField()
    pembuat             = models.ForeignKey('Pegawai', on_delete=models.CASCADE)
    kategori            = models.ForeignKey('Kategori', on_delete=models.SET_NULL,
                                            null=True, blank=True)
    status_dokumen      = models.CharField(max_length=20, default='Aktif')

    class Meta:
        abstract = True  # ABSTRAKSI — tidak bisa diinstansiasi langsung

    # ENKAPSULASI — status hanya boleh diubah lewat method ini
    def perbarui_status(self, status_baru):
        STATUS_VALID = ['Aktif', 'Kedaluwarsa', 'Dicabut']
        if status_baru not in STATUS_VALID:
            raise ValueError(f"Status tidak valid. Pilihan: {STATUS_VALID}")
        self.status_dokumen = status_baru
        self.save()

    # POLIMORFISME — di-override di tiap subclass
    def hitung_sisa_hari(self):
        selisih = self.tanggal_kedaluwarsa - timezone.now().date()
        return selisih.days

    def __str__(self):
        return f"{self.nomor_referensi} - {self.judul_dokumen}"


# ─── INHERITANCE + POLIMORFISME ───────────────────────────────────────────────
class DokumenHRD(DokumenDasar):
    JENIS_CHOICES = [
        ('Kontrak Kerja',      'Kontrak Kerja'),
        ('Surat Pengangkatan', 'Surat Pengangkatan'),
        ('Surat Peringatan',   'Surat Peringatan'),
        ('Sertifikat Pelatihan','Sertifikat Pelatihan'),
        ('Sertifikat K3',      'Sertifikat K3'),
        ('BPJS',               'BPJS'),
        ('Medical Check Up',   'Medical Check Up'),
        ('Dokumen Legal',      'Dokumen Legal'),
        ('Rekrutmen',          'Rekrutmen'),
        ('Lainnya',            'Lainnya'),
    ]
    departemen    = models.CharField(max_length=50, default='HRD')
    jenis_dokumen = models.CharField(max_length=50, choices=JENIS_CHOICES,
                                     default='Lainnya')

    # POLIMORFISME — HRD reminder 7 hari lebih awal
    def hitung_sisa_hari(self):
        selisih = self.tanggal_kedaluwarsa - timezone.now().date()
        return selisih.days - 7

    class Meta:
        verbose_name        = 'Dokumen HRD'
        verbose_name_plural = 'Dokumen HRD'


class DokumenStaff(DokumenDasar):
    JENIS_CHOICES = [
        ('KTP',                    'KTP'),
        ('SIM',                    'SIM'),
        ('Paspor',                 'Paspor'),
        ('Sertifikat Kerja',       'Sertifikat Kerja'),
        ('Kartu Identitas Karyawan','Kartu Identitas Karyawan'),
        ('Surat Izin Kerja',       'Surat Izin Kerja'),
        ('Lainnya',                'Lainnya'),
    ]
    pemilik       = models.ForeignKey('Pegawai', on_delete=models.CASCADE,
                                      related_name='dokumen_staff')
    jenis_dokumen = models.CharField(max_length=50, choices=JENIS_CHOICES,
                                     default='Lainnya')

    # POLIMORFISME — Staff reminder 14 hari lebih awal
    def hitung_sisa_hari(self):
        selisih = self.tanggal_kedaluwarsa - timezone.now().date()
        return selisih.days - 14

    class Meta:
        verbose_name        = 'Dokumen Staff'
        verbose_name_plural = 'Dokumen Staff'


# ─── PEGAWAI ─────────────────────────────────────────────────────────────────
class Pegawai(models.Model):
    GRUP_CHOICES = [
        ('Admin', 'Admin'),
        ('HRD',   'HRD'),
        ('Staff', 'Staff'),
    ]
    user          = models.OneToOneField(User, on_delete=models.CASCADE)
    nama_lengkap  = models.CharField(max_length=100)
    jabatan       = models.CharField(max_length=50)
    nomor_telepon = models.CharField(max_length=15, blank=True)
    kunci_otp     = models.CharField(max_length=32, default=pyotp.random_base32)
    grup_pengguna = models.CharField(max_length=20, choices=GRUP_CHOICES,
                                     default='Staff')

    def __str__(self):
        return f"{self.nama_lengkap} ({self.grup_pengguna})"


# ─── KATEGORI ────────────────────────────────────────────────────────────────
class Kategori(models.Model):
    URGENSI_CHOICES = [
        ('Rendah', 'Rendah'),
        ('Sedang', 'Sedang'),
        ('Tinggi', 'Tinggi'),
        ('Kritis', 'Kritis'),
    ]
    kode_kategori  = models.CharField(max_length=10, unique=True)
    nama_kategori  = models.CharField(max_length=50)
    level_urgensi  = models.CharField(max_length=20, choices=URGENSI_CHOICES,
                                      default='Sedang')
    deskripsi      = models.TextField()
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.kode_kategori}] {self.nama_kategori}"

    class Meta:
        verbose_name        = 'Kategori'
        verbose_name_plural = 'Kategori'
        ordering            = ['nama_kategori']


# ─── LOG AKTIVITAS ────────────────────────────────────────────────────────────
class LogAktivitas(models.Model):
    JENIS_AKSI_CHOICES = [
        ('Login',           'Login'),
        ('Logout',          'Logout'),
        ('Tambah Dokumen',  'Tambah Dokumen'),
        ('Edit Dokumen',    'Edit Dokumen'),
        ('Hapus Dokumen',   'Hapus Dokumen'),
        ('Tambah Pengguna', 'Tambah Pengguna'),
        ('Edit Pengguna',   'Edit Pengguna'),
        ('Hapus Pengguna',  'Hapus Pengguna'),
    ]
    id_catatan        = models.AutoField(primary_key=True)
    pegawai           = models.ForeignKey(Pegawai, on_delete=models.SET_NULL,
                                          null=True, blank=True)
    nama_pegawai      = models.CharField(max_length=100)
    jenis_aksi        = models.CharField(max_length=50, choices=JENIS_AKSI_CHOICES)
    referensi_dokumen = models.CharField(max_length=50, blank=True)
    keterangan        = models.TextField(blank=True)
    waktu_catatan     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.waktu_catatan:%d/%m/%Y %H:%M} | {self.nama_pegawai} | {self.jenis_aksi}"

    class Meta:
        verbose_name        = 'Log Aktivitas'
        verbose_name_plural = 'Log Aktivitas'
        ordering            = ['-waktu_catatan']
