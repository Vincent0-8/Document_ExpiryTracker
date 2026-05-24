from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from django.http import Http404
from .models import LogAktivitas, Kategori, DokumenHRD, DokumenStaff, Pegawai


# ─── HELPER: catat log otomatis ──────────────────────────────────────────────
def catat_log(request, jenis_aksi, referensi='', keterangan=''):
    """
    Panggil fungsi ini setiap ada aksi penting.
    Contoh: catat_log(request, 'Tambah Dokumen', 'HRD-001', 'Tambah kontrak Julianto')
    """
    try:
        pegawai = request.user.pegawai
        nama    = pegawai.nama_lengkap
    except Exception:
        pegawai = None
        nama    = request.user.username

    LogAktivitas.objects.create(
        pegawai           = pegawai,
        nama_pegawai      = nama,
        jenis_aksi        = jenis_aksi,
        referensi_dokumen = referensi,
        keterangan        = keterangan,
    )


# ─── MIXIN: hanya Admin ──────────────────────────────────────────────────────
class AdminOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Hanya user dengan grup_pengguna='Admin' yang bisa akses."""

    def test_func(self):
        try:
            return self.request.user.pegawai.grup_pengguna == 'Admin'
        except Exception:
            return False

    def handle_no_permission(self):
        return redirect('dashboard_utama')


# ─── MIXIN: Admin atau HRD ───────────────────────────────────────────────────
class AdminOrHRDMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Hanya Admin dan HRD yang bisa akses. Dipakai oleh Jacky (DokumenHRD)."""

    def test_func(self):
        try:
            return self.request.user.pegawai.grup_pengguna in ['Admin', 'HRD']
        except Exception:
            return False

    def handle_no_permission(self):
        return redirect('dashboard_utama')


# ─── DASHBOARD (scope: Damai) ─────────────────────────────────────────────────
@login_required
def dashboard_utama(request):
    return render(request, 'core/dashboard_utama.html')


@login_required
def dashboard_admin(request):
    hari_ini = timezone.now().date()
    context  = {
        'hrd_aktif'      : DokumenHRD.objects.filter(status_dokumen='Aktif').count(),
        'hrd_expired'    : DokumenHRD.objects.filter(status_dokumen='Kedaluwarsa').count(),
        'hrd_mau_expired': DokumenHRD.objects.filter(
            status_dokumen='Aktif',
            tanggal_kedaluwarsa__lte=hari_ini + timezone.timedelta(days=30)
        ).count(),
        'staff_aktif'    : DokumenStaff.objects.filter(status_dokumen='Aktif').count(),
        'staff_expired'  : DokumenStaff.objects.filter(status_dokumen='Kedaluwarsa').count(),
        'log_terbaru'    : LogAktivitas.objects.all()[:5],
    }
    return render(request, 'core/dashboard_admin.html', context)


@login_required
def monitoring(request):
    hari_ini = timezone.now().date()
    batas    = hari_ini + timezone.timedelta(days=30)
    context  = {
        'dokumen_hrd_expired'    : DokumenHRD.objects.filter(
            tanggal_kedaluwarsa__lt=hari_ini),
        'dokumen_hrd_mau_expired': DokumenHRD.objects.filter(
            tanggal_kedaluwarsa__range=(hari_ini, batas)),
        'dokumen_staff_expired'  : DokumenStaff.objects.filter(
            tanggal_kedaluwarsa__lt=hari_ini),
    }
    return render(request, 'core/monitoring.html', context)


@login_required
def dashboard_hrd(request):
    return render(request, 'core/dashboard_hrd.html')


@login_required
def dashboard_staff(request):
    hari_ini         = timezone.now().date()
    batas_peringatan = hari_ini + timezone.timedelta(days=14)

    try:
        pegawai  = request.user.pegawai
        is_admin = pegawai.grup_pengguna == 'Admin'
    except Exception:
        pegawai  = None
        is_admin = request.user.is_superuser

    if is_admin:
        qs = DokumenStaff.objects.all()
    elif pegawai:
        qs = DokumenStaff.objects.filter(pemilik=pegawai)
    else:
        qs = DokumenStaff.objects.none()

    context = {
        'total_dokumen'     : qs.count(),
        'dokumen_aktif'     : qs.filter(status_dokumen='Aktif').count(),
        'dokumen_expired'   : qs.filter(status_dokumen='Kedaluwarsa').count(),
        'hampir_expired'    : qs.filter(
            status_dokumen='Aktif',
            tanggal_kedaluwarsa__lte=batas_peringatan,
            tanggal_kedaluwarsa__gte=hari_ini,
        ).count(),
        'notifikasi_expired': qs.filter(
            status_dokumen='Aktif',
            tanggal_kedaluwarsa__lte=batas_peringatan,
        ).order_by('tanggal_kedaluwarsa')[:5],
        'pegawai'           : pegawai,
        'is_admin'          : is_admin,
    }
    return render(request, 'core/dashboard_staff.html', context)


def pengguna(request):
    return render(request, 'core/pengguna.html')

def doc_hrd(request):
    return render(request, 'core/doc_hrd.html')

def pengaturan(request):
    return render(request, 'core/pengaturan.html')


# ─── DOKUMEN STAFF (scope: Vincent) ─────────────────────────────────────────
class DokumenStaffListView(LoginRequiredMixin, ListView):
    model               = DokumenStaff
    template_name       = 'core/dokumen_staff_list.html'
    context_object_name = 'dokumens'
    paginate_by         = 10

    def get_queryset(self):
        try:
            pegawai  = self.request.user.pegawai
            is_admin = pegawai.grup_pengguna == 'Admin'
        except Exception:
            pegawai  = None
            is_admin = self.request.user.is_superuser

        if is_admin:
            qs = DokumenStaff.objects.all()
        elif pegawai:
            qs = DokumenStaff.objects.filter(pemilik=pegawai)
        else:
            qs = DokumenStaff.objects.none()

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(judul_dokumen__icontains=q) |
                Q(nomor_referensi__icontains=q)
            )

        jenis = self.request.GET.get('jenis', '').strip()
        if jenis:
            qs = qs.filter(jenis_dokumen=jenis)

        return qs.order_by('tanggal_kedaluwarsa')

    def get_context_data(self, **kwargs):
        ctx          = super().get_context_data(**kwargs)
        hari_ini     = timezone.now().date()
        ctx['hari_ini']    = hari_ini
        ctx['batas_warn']  = hari_ini + timezone.timedelta(days=14)
        ctx['q']           = self.request.GET.get('q', '')
        ctx['jenis_filter']= self.request.GET.get('jenis', '')
        ctx['jenis_choices']= DokumenStaff.JENIS_CHOICES
        return ctx


class DokumenStaffDetailView(LoginRequiredMixin, DetailView):
    model               = DokumenStaff
    template_name       = 'core/dokumen_staff_detail.html'
    context_object_name = 'dokumen'

    def get_object(self, queryset=None):
        obj = get_object_or_404(DokumenStaff, pk=self.kwargs['pk'])

        try:
            pegawai  = self.request.user.pegawai
            is_admin = pegawai.grup_pengguna == 'Admin'
        except Exception:
            pegawai  = None
            is_admin = self.request.user.is_superuser

        if not is_admin and obj.pemilik != pegawai:
            raise Http404("Dokumen tidak ditemukan atau Anda tidak memiliki akses.")

        return obj

    def get_context_data(self, **kwargs):
        ctx          = super().get_context_data(**kwargs)
        ctx['hari_ini']   = timezone.now().date()
        ctx['sisa_hari']  = self.object.hitung_sisa_hari()
        return ctx


# ─── KATEGORI (scope: Arsat) ─────────────────────────────────────────────────
class KategoriListView(AdminOnlyMixin, ListView):
    model                = Kategori
    template_name        = 'core/kategori_list.html'
    context_object_name  = 'kategoris'
    ordering             = ['nama_kategori']


class KategoriDetailView(AdminOnlyMixin, DetailView):
    model               = Kategori
    template_name       = 'core/kategori_detail.html'
    context_object_name = 'kategori'


class KategoriCreateView(AdminOnlyMixin, CreateView):
    model         = Kategori
    fields        = ['kode_kategori', 'nama_kategori', 'level_urgensi', 'deskripsi']
    template_name = 'core/kategori_form.html'
    success_url   = reverse_lazy('kategori_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['judul']  = 'Tambah Kategori'
        ctx['tombol'] = 'Simpan'
        return ctx

    def form_valid(self, form):
        # kode_kategori otomatis jadi huruf kapital
        form.instance.kode_kategori = form.instance.kode_kategori.upper()
        return super().form_valid(form)


class KategoriUpdateView(AdminOnlyMixin, UpdateView):
    model         = Kategori
    fields        = ['kode_kategori', 'nama_kategori', 'level_urgensi', 'deskripsi']
    template_name = 'core/kategori_form.html'
    success_url   = reverse_lazy('kategori_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['judul']  = 'Edit Kategori'
        ctx['tombol'] = 'Update'
        return ctx

    def form_valid(self, form):
        form.instance.kode_kategori = form.instance.kode_kategori.upper()
        return super().form_valid(form)


class KategoriDeleteView(AdminOnlyMixin, DeleteView):
    model         = Kategori
    template_name = 'core/kategori_confirm_delete.html'
    success_url   = reverse_lazy('kategori_list')


# ─── LOG AKTIVITAS (scope: Damai) ────────────────────────────────────────────
class LogAktivitasListView(AdminOnlyMixin, ListView):
    model               = LogAktivitas
    template_name       = 'core/log_aktivitas.html'
    context_object_name = 'logs'
    ordering            = ['-waktu_catatan']
    paginate_by         = 20


class DetailAktivitasView(AdminOnlyMixin, DetailView):
    model               = LogAktivitas
    template_name       = 'core/detail_aktivitas.html'
    context_object_name = 'log'
    pk_url_kwarg        = 'pk'


class RiwayatUserListView(AdminOnlyMixin, ListView):
    model               = LogAktivitas
    template_name       = 'core/riwayat_user.html'
    context_object_name = 'riwayat'
    paginate_by         = 20

    def get_queryset(self):
        # Filter by nama_pegawai dari query param
        # Contoh URL: /log_aktivitas/riwayat/?nama=Julianto
        nama = self.request.GET.get('nama')
        qs   = LogAktivitas.objects.all().order_by('-waktu_catatan')
        if nama:
            qs = qs.filter(nama_pegawai__icontains=nama)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nama_filter'] = self.request.GET.get('nama', '')
        return ctx
