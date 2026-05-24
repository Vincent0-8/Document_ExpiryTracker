from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Pegawai, Kategori, DokumenStaff
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generate dummy data for Dokumen Staff (Vincent jobdesk)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Memulai proses pembuatan data dummy...")

        # 1. Pastikan User Vincent ada
        try:
            user_vincent = User.objects.get(username='vincent')
            self.stdout.write(self.style.SUCCESS('User vincent ditemukan.'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User vincent tidak ditemukan! Pastikan sudah dibuat.'))
            return

        # 2. Pastikan Pegawai Vincent ada
        try:
            pegawai_vincent = Pegawai.objects.get(user=user_vincent)
            self.stdout.write(self.style.SUCCESS('Pegawai vincent ditemukan.'))
        except Pegawai.DoesNotExist:
            self.stdout.write(self.style.ERROR('Pegawai vincent tidak ditemukan!'))
            return

        # 3. Buat Kategori Dummy (jika belum ada)
        kategori_data = [
            {'kode': 'ID-CARD', 'nama': 'Kartu Identitas (KTP/SIM)'},
            {'kode': 'CERT-IT', 'nama': 'Sertifikat IT & Software'},
            {'kode': 'MED-CHK', 'nama': 'Hasil Medical Checkup'},
        ]
        
        kategori_objs = []
        for kat in kategori_data:
            obj, created = Kategori.objects.get_or_create(
                kode_kategori=kat['kode'],
                defaults={'nama_kategori': kat['nama'], 'deskripsi': 'Dummy kategori'}
            )
            kategori_objs.append(obj)
        self.stdout.write(self.style.SUCCESS('Kategori dummy siap.'))

        # 4. Hapus dokumen lama Vincent agar tidak menumpuk
        DokumenStaff.objects.filter(pemilik=pegawai_vincent).delete()
        self.stdout.write('Dokumen lama vincent dihapus.')

        # 5. Buat Dokumen Dummy
        hari_ini = timezone.now().date()
        
        dokumen_list = [
            {
                'judul': 'KTP - Vincent',
                'jenis': 'KTP',
                'kat': kategori_objs[0],
                'status': 'Aktif',
                'berlaku': hari_ini - timedelta(days=365),
                'kadaluarsa': hari_ini + timedelta(days=1000) # Aman (Jauh)
            },
            {
                'judul': 'SIM C - Vincent',
                'jenis': 'SIM',
                'kat': kategori_objs[0],
                'status': 'Aktif',
                'berlaku': hari_ini - timedelta(days=1800),
                'kadaluarsa': hari_ini + timedelta(days=10) # Hampir Expired
            },
            {
                'judul': 'Sertifikat AWS Cloud',
                'jenis': 'Sertifikat',
                'kat': kategori_objs[1],
                'status': 'Kedaluwarsa',
                'berlaku': hari_ini - timedelta(days=1000),
                'kadaluarsa': hari_ini - timedelta(days=5) # Expired
            },
            {
                'judul': 'Paspor - Vincent',
                'jenis': 'Paspor',
                'kat': kategori_objs[0],
                'status': 'Aktif',
                'berlaku': hari_ini - timedelta(days=300),
                'kadaluarsa': hari_ini + timedelta(days=2) # Hampir Expired (Sangat dekat)
            },
            {
                'judul': 'Medical Checkup 2025',
                'jenis': 'Lainnya',
                'kat': kategori_objs[2],
                'status': 'Aktif',
                'berlaku': hari_ini - timedelta(days=10),
                'kadaluarsa': hari_ini + timedelta(days=355) # Aman
            }
        ]

        for i, doc in enumerate(dokumen_list):
            DokumenStaff.objects.create(
                nomor_referensi=f'DOC-STF-VIN-{100+i}',
                judul_dokumen=doc['judul'],
                jenis_dokumen=doc['jenis'],
                kategori=doc['kat'],
                pemilik=pegawai_vincent,
                pembuat=pegawai_vincent,
                tanggal_berlaku=doc['berlaku'],
                tanggal_kedaluwarsa=doc['kadaluarsa'],
                status_dokumen=doc['status']
            )

        self.stdout.write(self.style.SUCCESS(f'Berhasil membuat {len(dokumen_list)} dokumen dummy untuk Vincent!'))
        self.stdout.write(self.style.SUCCESS('Silakan cek http://127.0.0.1:8000/dashboard_staff/'))
