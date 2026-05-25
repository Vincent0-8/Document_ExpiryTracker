from django.urls import path
from . import views

urlpatterns = [
    # ── Dashboard (scope: Damai) ─────────────────────────────────────────────
    path('dashboard_utama/', views.dashboard_utama,  name='dashboard_utama'),
    path('dashboard_admin/', views.dashboard_admin,  name='core_dashboard_admin'),
    path('core/hrd/',        views.dashboard_hrd,    name='core_dashboard_hrd'),
    path('core/staff/',      views.dashboard_staff,  name='core_dashboard_staff'),
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

    # ── Dokumen HRD dengan desain Jacky (backup templates) ──────────────────
    path('hrd/',
         views.HRDDashboardView.as_view(),     name='hrd_dashboard'),
    path('hrd/dokumen/',
         views.HRDDokumenListView.as_view(),   name='hrd_dokumen_list'),
    path('hrd/dokumen/tambah/',
         views.HRDDokumenCreateView.as_view(), name='hrd_dokumen_tambah'),
    path('hrd/dokumen/<int:pk>/',
         views.HRDDokumenDetailView.as_view(), name='hrd_dokumen_detail'),
    path('hrd/dokumen/<int:pk>/edit/',
         views.HRDDokumenUpdateView.as_view(), name='hrd_dokumen_edit'),
    path('hrd/dokumen/<int:pk>/hapus/',
         views.HRDDokumenDeleteView.as_view(), name='hrd_dokumen_hapus'),

    # ── Dokumen HRD alternatif (desain baru merged) ──────────────────────────
    path('doc_hrd/',
         views.DokumenHRDListView.as_view(),   name='doc_hrd_list'),
    path('doc_hrd/tambah/',
         views.DokumenHRDCreateView.as_view(), name='doc_hrd_tambah'),
    path('doc_hrd/<int:pk>/',
         views.DokumenHRDDetailView.as_view(), name='doc_hrd_detail'),
    path('doc_hrd/<int:pk>/edit/',
         views.DokumenHRDUpdateView.as_view(), name='doc_hrd_edit'),
    path('doc_hrd/<int:pk>/hapus/',
         views.DokumenHRDDeleteView.as_view(), name='doc_hrd_hapus'),

    # ── Dokumen Staff (scope: Vincent) ───────────────────────────────────────
    path('doc_staff/',
         views.DokumenStaffListView.as_view(),   name='doc_staff'),
    path('doc_staff/tambah/',
         views.DokumenStaffCreateView.as_view(), name='doc_staff_tambah'),
    path('doc_staff/<int:pk>/',
         views.DokumenStaffDetailView.as_view(), name='doc_staff_detail'),
    path('doc_staff/<int:pk>/edit/',
         views.DokumenStaffUpdateView.as_view(), name='doc_staff_edit'),
    path('doc_staff/<int:pk>/hapus/',
         views.DokumenStaffDeleteView.as_view(), name='doc_staff_hapus'),

    # ── Redirect helpers ────────────────────────────────────────────────────
    path('pengguna/',   views.pengguna,   name='pengguna'),
    path('doc_hrd_redirect/', views.doc_hrd, name='doc_hrd'),
    path('pengaturan/', views.pengaturan, name='pengaturan'),
]
