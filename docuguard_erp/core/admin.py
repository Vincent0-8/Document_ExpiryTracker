from django.contrib import admin
from .models import Pegawai, Kategori, DokumenHRD, DokumenFinance, LogAktivitas

admin.site.register(Pegawai)
admin.site.register(Kategori)
admin.site.register(DokumenHRD)
admin.site.register(DokumenFinance)
admin.site.register(LogAktivitas)