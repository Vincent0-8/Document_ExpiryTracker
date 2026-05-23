from django.urls import path
from . import views

urlpatterns = [
    path('dashboard_utama/', views.dashboard_utama, name='dashboard_utama'),
    path('dashboard_admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard_hrd/', views.dashboard_hrd, name='dashboard_hrd'),  
    path('dashboard_staff/', views.dashboard_staff, name='dashboard_staff'),
    path('monitoring/', views.monitoring, name='monitoring'),
    
    # Log Aktivitas (3 halaman scope)
    path('log_aktivitas/',views.LogAktivitasListView.as_view(),name='log_aktivitas'),
    path('log_aktivitas/riwayat_user/<int:pk>/', views.RiwayatUserListView.as_view(), name='riwayat_user'),        # ← tambah
    path('log_aktivitas/detail_aktivitas/<int:pk>/', views.DetailAktivitasView.as_view(), name='detail_aktivitas'),     # ← ganti id → pk

    # Manajemen
    path('pengguna/', views.pengguna, name='pengguna'),
    path('kategori/', views.kategori, name='kategori'),
    path('dok_hrd/', views.dok_hrd, name='dok_hrd'),
    path('dok_staff/', views.dok_staff, name='dok_staff'),
    path('pengaturan/', views.pengaturan, name='pengaturan'),
]