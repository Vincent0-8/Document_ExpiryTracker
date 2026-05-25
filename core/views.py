from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
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
        # Support CustomUser (Julianto) yang punya get_full_name()
        nama = request.user.get_full_name() or request.user.username
        # Coba ambil Pegawai jika ada (core model)
        pegawai = getattr(request.user, 'pegawai', None)
        if pegawai and not nama:
            nama = pegawai.nama_lengkap
    except Exception:
        pegawai = None
        nama = request.user.username

    LogAktivitas.objects.create(
        pegawai           = None,  # FK ke Pegawai (core) — opsional
        nama_pegawai      = nama,
        jenis_aksi        = jenis_aksi,
        referensi_dokumen = referensi,
        keterangan        = keterangan,
    )


# ─── MIXIN: hanya Admin ──────────────────────────────────────────────────────
class AdminOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Hanya Admin yang boleh akses. Cek via CustomUser.is_admin_role."""

    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.is_admin_role

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('authentication:login')
        return redirect('authentication:dashboard')


# ─── MIXIN: Admin atau HRD ───────────────────────────────────────────────────
class AdminOrHRDMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Hanya Admin dan HRD yang bisa akses. Dipakai oleh Jacky (DokumenHRD)."""

    def test_func(self):
        return self.request.user.is_authenticated and \
               (self.request.user.is_admin_role or self.request.user.is_hrd_role)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('authentication:login')
        return redirect('authentication:dashboard')


# ─── DASHBOARD (scope: Damai) ─────────────────────────────────────────────────
@login_required
def dashboard_utama(request):
    return render(request, 'core/dashboard_utama.html')


@login_required
def dashboard_admin(request):
    if not request.user.is_admin_role:
        return redirect('authentication:dashboard')
    from authentication.models import CustomUser
    hari_ini = timezone.now().date()
    context  = {
        # Stat dokumen
        'hrd_aktif'      : DokumenHRD.objects.filter(status_dokumen='Aktif').count(),
        'hrd_expired'    : DokumenHRD.objects.filter(status_dokumen='Kedaluwarsa').count(),
        'hrd_mau_expired': DokumenHRD.objects.filter(
            status_dokumen='Aktif',
            tanggal_kedaluwarsa__lte=hari_ini + timezone.timedelta(days=30)
        ).count(),
        'staff_aktif'    : DokumenStaff.objects.filter(status_dokumen='Aktif').count(),
        'staff_expired'  : DokumenStaff.objects.filter(status_dokumen='Kedaluwarsa').count(),
        'log_terbaru'    : LogAktivitas.objects.all()[:5],
        # Stat user (dari authentication)
        'total_users'    : CustomUser.objects.count(),
        'total_admin'    : CustomUser.objects.filter(role=CustomUser.Role.ADMIN).count(),
        'total_hrd'      : CustomUser.objects.filter(role=CustomUser.Role.HRD).count(),
        'total_staff'    : CustomUser.objects.filter(role=CustomUser.Role.STAFF).count(),
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


# ─── Placeholder views untuk scope anggota lain (Jacky & Vincent) ────────────
# CATATAN: Jacky dan Vincent perlu membuat template dan views penuh untuk ini.
# Sementara diarahkan ke dashboard masing-masing.
@login_required
def dashboard_hrd(request):
    # Placeholder — Jacky akan mengisi ini dengan DokumenHRD CRUD
    return redirect('authentication:dashboard_hrd')


@login_required
def dashboard_staff(request):
    hari_ini         = timezone.now().date()
    batas_peringatan = hari_ini + timezone.timedelta(days=14)
    is_admin         = request.user.is_admin_role

    try:
        pegawai = request.user.pegawai
    except Exception:
        pegawai = None

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


@login_required
def pengguna(request):
    # Diarahkan ke user list milik Julianto
    return redirect('authentication:user_list')


@login_required
def doc_hrd(request):
    return redirect('authentication:dashboard_hrd')


@login_required
def pengaturan(request):
    return redirect('authentication:profile')


# ─── DOKUMEN STAFF (scope: Vincent) ──────────────────────────────────────────
class DokumenStaffListView(LoginRequiredMixin, ListView):
    model               = DokumenStaff
    template_name       = 'core/dokumen_staff_list.html'
    context_object_name = 'dokumens'
    paginate_by         = 10

    def get_queryset(self):
        is_admin = self.request.user.is_admin_role
        try:
            pegawai = self.request.user.pegawai
        except Exception:
            pegawai = None

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
        ctx              = super().get_context_data(**kwargs)
        hari_ini         = timezone.now().date()
        ctx['hari_ini']     = hari_ini
        ctx['batas_warn']   = hari_ini + timezone.timedelta(days=14)
        ctx['q']            = self.request.GET.get('q', '')
        ctx['jenis_filter'] = self.request.GET.get('jenis', '')
        ctx['jenis_choices']= DokumenStaff.JENIS_CHOICES
        return ctx


class DokumenStaffDetailView(LoginRequiredMixin, DetailView):
    model               = DokumenStaff
    template_name       = 'core/dokumen_staff_detail.html'
    context_object_name = 'dokumen'

    def get_object(self, queryset=None):
        obj      = get_object_or_404(DokumenStaff, pk=self.kwargs['pk'])
        is_admin = self.request.user.is_admin_role
        try:
            pegawai = self.request.user.pegawai
        except Exception:
            pegawai = None

        if not is_admin and obj.pemilik != pegawai:
            raise Http404("Dokumen tidak ditemukan atau Anda tidak memiliki akses.")
        return obj

    def get_context_data(self, **kwargs):
        ctx             = super().get_context_data(**kwargs)
        ctx['hari_ini'] = timezone.now().date()
        ctx['sisa_hari']= self.object.hitung_sisa_hari()
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

    def get_queryset(self):
        qs = super().get_queryset()
        aksi   = self.request.GET.get('aksi', '').strip()
        search = self.request.GET.get('search', '').strip()
        if aksi:
            qs = qs.filter(jenis_aksi=aksi)
        if search:
            qs = qs.filter(nama_pegawai__icontains=search)
        return qs


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
        nama = self.request.GET.get('nama')
        qs   = LogAktivitas.objects.all().order_by('-waktu_catatan')
        if nama:
            qs = qs.filter(nama_pegawai__icontains=nama)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nama_filter'] = self.request.GET.get('nama', '')
        return ctx

# ─── DOKUMEN HRD (scope: Jacky) ──────────────────────────────────────────────
from .forms import DokumenHRDForm, DokumenStaffForm


class DokumenHRDListView(AdminOrHRDMixin, ListView):
    model               = DokumenHRD
    template_name       = 'core/dokumen_hrd_list.html'
    context_object_name = 'dokumens'
    paginate_by         = 10

    def get_queryset(self):
        qs = DokumenHRD.objects.all()
        q      = self.request.GET.get('q', '').strip()
        jenis  = self.request.GET.get('jenis', '').strip()
        status = self.request.GET.get('status', '').strip()
        if q:
            qs = qs.filter(
                Q(judul_dokumen__icontains=q) |
                Q(nomor_referensi__icontains=q)
            )
        if jenis:
            qs = qs.filter(jenis_dokumen=jenis)
        if status:
            qs = qs.filter(status_dokumen=status)
        return qs.order_by('tanggal_kedaluwarsa')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hari_ini = timezone.now().date()
        ctx['hari_ini']      = hari_ini
        ctx['batas_warn']    = hari_ini + timezone.timedelta(days=37)  # 30+7 hari
        ctx['q']             = self.request.GET.get('q', '')
        ctx['jenis_filter']  = self.request.GET.get('jenis', '')
        ctx['status_filter'] = self.request.GET.get('status', '')
        ctx['jenis_choices'] = DokumenHRD.JENIS_CHOICES
        ctx['status_choices'] = ['Aktif', 'Kedaluwarsa', 'Dicabut']
        return ctx


class DokumenHRDDetailView(AdminOrHRDMixin, DetailView):
    model               = DokumenHRD
    template_name       = 'core/dokumen_hrd_detail.html'
    context_object_name = 'dokumen'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['hari_ini']  = timezone.now().date()
        ctx['sisa_hari'] = self.object.hitung_sisa_hari()
        return ctx


class DokumenHRDCreateView(AdminOrHRDMixin, CreateView):
    model         = DokumenHRD
    form_class    = DokumenHRDForm
    template_name = 'core/dokumen_hrd_form.html'
    success_url   = reverse_lazy('doc_hrd_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['judul_halaman'] = 'Tambah Dokumen HRD'
        ctx['action_label']  = 'Simpan'
        ctx['is_edit']       = False
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        catat_log(self.request, 'Tambah Dokumen',
                  self.object.nomor_referensi,
                  f'Tambah DokumenHRD: {self.object.judul_dokumen}')
        return response


class DokumenHRDUpdateView(AdminOrHRDMixin, UpdateView):
    model         = DokumenHRD
    form_class    = DokumenHRDForm
    template_name = 'core/dokumen_hrd_form.html'
    success_url   = reverse_lazy('doc_hrd_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['judul_halaman'] = f'Edit: {self.object.judul_dokumen}'
        ctx['action_label']  = 'Perbarui'
        ctx['is_edit']       = True
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        catat_log(self.request, 'Edit Dokumen',
                  self.object.nomor_referensi,
                  f'Edit DokumenHRD: {self.object.judul_dokumen}')
        return response


class DokumenHRDDeleteView(AdminOrHRDMixin, DeleteView):
    model               = DokumenHRD
    template_name       = 'core/dokumen_hrd_hapus.html'
    success_url         = reverse_lazy('doc_hrd_list')
    context_object_name = 'dokumen'

    def form_valid(self, form):
        nama = self.object.judul_dokumen
        ref  = self.object.nomor_referensi
        response = super().form_valid(form)
        catat_log(self.request, 'Hapus Dokumen', ref, f'Hapus DokumenHRD: {nama}')
        return response


# ─── DOKUMEN STAFF CRUD (tambahan untuk Vincent) ─────────────────────────────
class DokumenStaffCreateView(LoginRequiredMixin, CreateView):
    model         = DokumenStaff
    form_class    = DokumenStaffForm
    template_name = 'core/dokumen_staff_form.html'
    success_url   = reverse_lazy('doc_staff')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['judul_halaman'] = 'Tambah Dokumen Staff'
        ctx['action_label']  = 'Simpan'
        ctx['is_edit']       = False
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        catat_log(self.request, 'Tambah Dokumen',
                  self.object.nomor_referensi,
                  f'Tambah DokumenStaff: {self.object.judul_dokumen}')
        return response


class DokumenStaffUpdateView(LoginRequiredMixin, UpdateView):
    model         = DokumenStaff
    form_class    = DokumenStaffForm
    template_name = 'core/dokumen_staff_form.html'
    success_url   = reverse_lazy('doc_staff')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['judul_halaman'] = f'Edit: {self.object.judul_dokumen}'
        ctx['action_label']  = 'Perbarui'
        ctx['is_edit']       = True
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        catat_log(self.request, 'Edit Dokumen',
                  self.object.nomor_referensi,
                  f'Edit DokumenStaff: {self.object.judul_dokumen}')
        return response


class DokumenStaffDeleteView(LoginRequiredMixin, DeleteView):
    model               = DokumenStaff
    template_name       = 'core/dokumen_staff_hapus.html'
    success_url         = reverse_lazy('doc_staff')
    context_object_name = 'dokumen'

    def form_valid(self, form):
        nama = self.object.judul_dokumen
        ref  = self.object.nomor_referensi
        response = super().form_valid(form)
        catat_log(self.request, 'Hapus Dokumen', ref, f'Hapus DokumenStaff: {nama}')
        return response


# ─── VIEWS HRD (pakai template desain dari backup/Jacky) ─────────────────────
from .forms import DokumenHRDForm as _DokumenHRDForm
from django.db.models import Count as _Count


class HRDDashboardView(AdminOrHRDMixin, TemplateView):
    """Dashboard HRD dengan desain asli Jacky (dari backup)."""
    template_name = 'core/hrd/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx     = super().get_context_data(**kwargs)
        semua   = DokumenHRD.objects.all()
        hari_ini = timezone.now().date()

        ctx['total_dokumen']          = semua.count()
        ctx['dokumen_aktif']          = semua.filter(status_dokumen='Aktif').count()
        ctx['dokumen_hampir_expired'] = semua.filter(
            status_dokumen='Aktif',
            tanggal_kedaluwarsa__lte=hari_ini + timezone.timedelta(days=30),
            tanggal_kedaluwarsa__gte=hari_ini,
        ).count()
        ctx['dokumen_expired']        = semua.filter(status_dokumen='Kedaluwarsa').count()
        ctx['reminder_list']          = semua.filter(
            tanggal_kedaluwarsa__lte=hari_ini + timezone.timedelta(days=30),
            tanggal_kedaluwarsa__gte=hari_ini,
        ).order_by('tanggal_kedaluwarsa')[:8]
        ctx['dokumen_terbaru']        = semua.order_by('-id')[:6]
        ctx['stats_jenis']            = semua.values('jenis_dokumen').annotate(jumlah=_Count('id')).order_by('-jumlah')
        ctx['total_dokumen']          = semua.count()
        return ctx


class HRDDokumenListView(AdminOrHRDMixin, ListView):
    """Daftar Dokumen HRD - desain asli Jacky."""
    model               = DokumenHRD
    template_name       = 'core/hrd/list.html'
    context_object_name = 'dokumen_list'
    paginate_by         = 10

    def get_queryset(self):
        qs     = DokumenHRD.objects.all()
        q      = self.request.GET.get('q', '').strip()
        jenis  = self.request.GET.get('jenis', '').strip()
        status = self.request.GET.get('status', '').strip()
        if q:
            qs = qs.filter(
                Q(judul_dokumen__icontains=q) |
                Q(nomor_referensi__icontains=q)
            )
        if jenis:
            qs = qs.filter(jenis_dokumen=jenis)
        if status:
            qs = qs.filter(status_dokumen=status)
        return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q']             = self.request.GET.get('q', '')
        ctx['jenis_filter']  = self.request.GET.get('jenis', '')
        ctx['status_filter'] = self.request.GET.get('status', '')
        ctx['jenis_choices'] = DokumenHRD.JENIS_CHOICES
        ctx['status_choices'] = ['Aktif', 'Kedaluwarsa', 'Dicabut']
        return ctx


class HRDDokumenDetailView(AdminOrHRDMixin, DetailView):
    """Detail Dokumen HRD - desain asli Jacky."""
    model               = DokumenHRD
    template_name       = 'core/hrd/detail.html'
    context_object_name = 'dokumen'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sisa_hari'] = self.object.hitung_sisa_hari()
        return ctx


class HRDDokumenCreateView(AdminOrHRDMixin, CreateView):
    """Tambah Dokumen HRD - desain asli Jacky."""
    model         = DokumenHRD
    form_class    = _DokumenHRDForm
    template_name = 'core/hrd/form.html'
    success_url   = reverse_lazy('hrd_dokumen_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['judul_halaman'] = 'Tambah Dokumen HRD'
        ctx['action_label']  = 'Simpan Dokumen'
        ctx['is_edit']       = False
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        catat_log(self.request, 'Tambah Dokumen',
                  self.object.nomor_referensi,
                  f'Tambah: {self.object.judul_dokumen}')
        return response


class HRDDokumenUpdateView(AdminOrHRDMixin, UpdateView):
    """Edit Dokumen HRD - desain asli Jacky."""
    model         = DokumenHRD
    form_class    = _DokumenHRDForm
    template_name = 'core/hrd/form.html'
    success_url   = reverse_lazy('hrd_dokumen_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['judul_halaman'] = f'Edit: {self.object.judul_dokumen}'
        ctx['action_label']  = 'Perbarui'
        ctx['is_edit']       = True
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        catat_log(self.request, 'Edit Dokumen',
                  self.object.nomor_referensi,
                  f'Edit: {self.object.judul_dokumen}')
        return response


class HRDDokumenDeleteView(AdminOrHRDMixin, DeleteView):
    """Hapus Dokumen HRD - desain asli Jacky."""
    model               = DokumenHRD
    template_name       = 'core/hrd/hapus.html'
    success_url         = reverse_lazy('hrd_dokumen_list')
    context_object_name = 'dokumen'

    def form_valid(self, form):
        nama = self.object.judul_dokumen
        ref  = self.object.nomor_referensi
        response = super().form_valid(form)
        catat_log(self.request, 'Hapus Dokumen', ref, f'Hapus: {nama}')
        return response
