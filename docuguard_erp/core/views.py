
# Create your views here.
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import LogAktivitas

from django.shortcuts import redirect

def test_func(self):
    return self.request.user.is_staff

def handle_no_permission(self):
    return redirect('dashboard_utama')

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

def kategori(request):
    return render(request, 'core/kategori.html')

class LogAktivitasListView(ListView):
    template_name = 'core/log_aktivitas.html'
    context_object_name = 'logs'

    def get_queryset(self):
        return [] 

def pengguna(request):
    return render(request, 'core/pengguna.html')

def dok_hrd(request):
    return render(request, 'core/dok_hrd.html')

def dok_staff(request):
    return render(request, 'core/dok_staff.html')

class DetailAktivitasView(DetailView):
    template_name = 'core/detail_aktivitas.html'
    context_object_name = 'log'

    def get_object(self):
        return {'id': self.kwargs['pk']}

class RiwayatUserListView(ListView):
    template_name = 'core/riwayat_user.html'
    context_object_name = 'riwayat'

    def get_queryset(self):
        return []

def pengaturan(request):
    return render(request, 'core/pengaturan.html')  
        
