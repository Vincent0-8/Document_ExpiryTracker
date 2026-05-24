# Create your views here.
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import LogAktivitas, Kategori


# ─── Mixin: hanya Admin yang boleh akses ────────────────────────────────────
class AdminOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Hanya user dengan grup_pengguna='Admin' yang bisa akses view ini."""

    def test_func(self):
        try:
            return self.request.user.pegawai.grup_pengguna == 'Admin'
        except Exception:
            return False

    def handle_no_permission(self):
        return redirect('dashboard_utama')

class AdminOrHRDMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Hanya Admin dan HRD yang bisa akses."""

    def test_func(self):
        try:
            return self.request.user.pegawai.grup_pengguna in ['Admin', 'HRD']
        except Exception:
            return False

    def handle_no_permission(self):
        return redirect('dashboard_utama')
    
# ─── Dashboard views ─────────────────────────────────────────────────────────
def dashboard_admin(request):
    return render(request, 'core/dashboard_admin.html')

def monitoring(request):
    return render(request, 'core/monitoring.html')

def dashboard_utama(request):
    return render(request, 'core/dashboard_utama.html')

def dashboard_hrd(request):
    return render(request, 'core/dashboard_hrd.html')

def dashboard_staff(request):
    return render(request, 'core/dashboard_staff.html')

def pengguna(request):
    return render(request, 'core/pengguna.html')

def doc_hrd(request):
    return render(request, 'core/doc_hrd.html')

def doc_staff(request):
    return render(request, 'core/doc_staff.html')

def pengaturan(request):
    return render(request, 'core/pengaturan.html')


# ─── CRUD Kategori (CBV — scope Arsat) ───────────────────────────────────────
class KategoriListView(AdminOnlyMixin, ListView):
    model = Kategori
    template_name = 'core/kategori_list.html'
    context_object_name = 'kategoris'
    ordering = ['nama_kategori']


class KategoriDetailView(AdminOnlyMixin, DetailView):
    model = Kategori
    template_name = 'core/kategori_detail.html'
    context_object_name = 'kategori'


class KategoriCreateView(AdminOnlyMixin, CreateView):
    model = Kategori
    fields = ['kode_kategori', 'nama_kategori', 'level_urgensi', 'deskripsi']
    template_name = 'core/kategori_form.html'
    success_url = reverse_lazy('kategori_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['judul'] = 'Tambah Kategori'
        ctx['tombol'] = 'Simpan'
        return ctx

    def form_valid(self, form):
        # kode_kategori otomatis jadi huruf kapital semua
        form.instance.kode_kategori = form.instance.kode_kategori.upper()
        return super().form_valid(form)

class KategoriUpdateView(AdminOnlyMixin, UpdateView):
    model = Kategori
    fields = ['kode_kategori', 'nama_kategori', 'level_urgensi', 'deskripsi']
    template_name = 'core/kategori_form.html'
    success_url = reverse_lazy('kategori_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['judul'] = 'Edit Kategori'
        ctx['tombol'] = 'Update'
        return ctx

    def form_valid(self, form):
        form.instance.kode_kategori = form.instance.kode_kategori.upper()
        return super().form_valid(form)
    
class KategoriDeleteView(AdminOnlyMixin, DeleteView):
    model = Kategori
    template_name = 'core/kategori_confirm_delete.html'
    success_url = reverse_lazy('kategori_list')


# ─── Log Aktivitas (CBV — scope Damai, diperbaiki Arsat) ────────────────────
class LogAktivitasListView(AdminOnlyMixin, ListView):
    model = LogAktivitas
    template_name = 'core/log_aktivitas.html'
    context_object_name = 'logs'
    ordering = ['-waktu_catatan']
    paginate_by = 20


class DetailAktivitasView(AdminOnlyMixin, DetailView):
    model = LogAktivitas
    template_name = 'core/detail_aktivitas.html'
    context_object_name = 'log'
    pk_url_kwarg = 'pk'


class RiwayatUserListView(AdminOnlyMixin, ListView):
    model = LogAktivitas
    template_name = 'core/riwayat_user.html'
    context_object_name = 'riwayat'
    ordering = ['-waktu_catatan']
    paginate_by = 20

    def get_queryset(self):
        # filter berdasarkan nama pegawai dari query param
        # contoh URL: /log_aktivitas/riwayat/?nama=Julianto
        nama = self.request.GET.get('nama')
        qs = LogAktivitas.objects.all().order_by('-waktu_catatan')
        if nama:
            qs = qs.filter(nama_pegawai__icontains=nama)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nama_filter'] = self.request.GET.get('nama', '')
        return ctx