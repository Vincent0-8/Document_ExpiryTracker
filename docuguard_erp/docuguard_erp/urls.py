"""
docuguard_erp/urls.py — URL utama project.

CARA INTEGRASI ANGGOTA LAIN:
Setiap anggota cukup tambahkan satu baris path() di sini.
Contoh Jacky: path('hrd/', include('documents_hrd.urls', namespace='hrd')),
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    # Admin Django bawaan
    path('admin/', admin.site.urls),

    # ─── Authentication & User Management (Julianto) ───
    path('auth/', include('authentication.urls', namespace='authentication')),

    # ─── Redirect root ke dashboard ───
    path('', lambda request: redirect('authentication:login'), name='home'),

    # ─── Tambahkan app anggota lain di sini (jangan ubah yang sudah ada) ───
    # path('hrd/', include('documents_hrd.urls', namespace='hrd')),       # Jacky
    # path('staff/', include('documents_staff.urls', namespace='staff')), # Vincent
    # path('log/', include('dashboard.urls', namespace='dashboard')),     # Damai
    # path('categories/', include('categories.urls', namespace='categories')), # Arsat
]

# Serve media files saat development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
