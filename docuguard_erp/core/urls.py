from django.urls import path
from . import views

urlpatterns = [
    # ── Dashboard (scope: Damai) ─────────────────────────────────────────────
    path('dashboard_utama/', views.dashboard_utama,  name='dashboard_utama'),
    path('dashboard_admin/', views.dashboard_admin,  name='dashboard_admin'),
    path('dashboard_hrd/',   views.dashboard_hrd,    name='dashboard_hrd'),
    path('dashboard_staff/', views.dashboard_staff,  name='dashboard_staff'),
    path('monitoring/',      views.monitoring,        name='monitoring'),

    # ── Log Aktivitas (scope: Damai) ─────────────────────────────────────────
    path('log_aktivitas/',
         views.LogAktivitasListView.as_view(), name='log_aktivitas'),
    path('log_aktivitas/riwayat/',
         views.RiwayatUserListView.as_view(),  name='riwayat_user'),
    path('log_aktivitas/<int:pk>/',
         views.DetailAktivitasView.as_view(),  name='detail_aktivitas'),

    # ── Kategori (scope: Arsat) ──────────────────────────────────────────────
    path('kategori/',
         views.KategoriListView.as_view(),   name='kategori_list'),
    path('kategori/tambah/',
         views.KategoriCreateView.as_view(), name='kategori_tambah'),
    path('kategori/<int:pk>/',
         views.KategoriDetailView.as_view(), name='kategori_detail'),
    path('kategori/<int:pk>/edit/',
         views.KategoriUpdateView.as_view(), name='kategori_edit'),
    path('kategori/<int:pk>/hapus/',
         views.KategoriDeleteView.as_view(), name='kategori_hapus'),

    # ── Placeholder untuk scope anggota lain ────────────────────────────────
    path('pengguna/',   views.pengguna,   name='pengguna'),
    path('doc_hrd/',    views.doc_hrd,    name='doc_hrd'),
    path('doc_staff/',  views.doc_staff,  name='doc_staff'),
    path('pengaturan/', views.pengaturan, name='pengaturan'),
]
