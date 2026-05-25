from django import forms
from .models import DokumenHRD, DokumenStaff


class DokumenHRDForm(forms.ModelForm):
    class Meta:
        model  = DokumenHRD
        fields = [
            'nomor_referensi', 'judul_dokumen', 'jenis_dokumen',
            'file_lampiran', 'tanggal_berlaku', 'tanggal_kedaluwarsa',
        ]
        widgets = {
            'nomor_referensi':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HRD-2024-001'}),
            'judul_dokumen':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Judul dokumen'}),
            'jenis_dokumen':       forms.Select(attrs={'class': 'form-select'}),
            'file_lampiran':       forms.FileInput(attrs={'class': 'form-control'}),
            'tanggal_berlaku':     forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'tanggal_kedaluwarsa': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            if self.instance.tanggal_berlaku:
                self.initial['tanggal_berlaku'] = self.instance.tanggal_berlaku.strftime('%Y-%m-%d')
            if self.instance.tanggal_kedaluwarsa:
                self.initial['tanggal_kedaluwarsa'] = self.instance.tanggal_kedaluwarsa.strftime('%Y-%m-%d')

    def clean(self):
        cleaned     = super().clean()
        berlaku     = cleaned.get('tanggal_berlaku')
        kedaluwarsa = cleaned.get('tanggal_kedaluwarsa')
        if berlaku and kedaluwarsa and kedaluwarsa <= berlaku:
            raise forms.ValidationError('Tanggal kedaluwarsa harus setelah tanggal berlaku.')
        return cleaned


class DokumenStaffForm(forms.ModelForm):
    class Meta:
        model  = DokumenStaff
        fields = [
            'nomor_referensi', 'judul_dokumen', 'jenis_dokumen',
            'pemilik','file_lampiran', 'tanggal_berlaku', 'tanggal_kedaluwarsa',
        ]
        widgets = {
            'nomor_referensi':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'STF-2024-001'}),
            'judul_dokumen':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Judul dokumen'}),
            'jenis_dokumen':       forms.Select(attrs={'class': 'form-select'}),
            'pemilik':             forms.Select(attrs={'class': 'form-select'}),
            'file_lampiran':       forms.FileInput(attrs={'class': 'form-control'}),
            'tanggal_berlaku':     forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'tanggal_kedaluwarsa': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            if self.instance.tanggal_berlaku:
                self.initial['tanggal_berlaku'] = self.instance.tanggal_berlaku.strftime('%Y-%m-%d')
            if self.instance.tanggal_kedaluwarsa:
                self.initial['tanggal_kedaluwarsa'] = self.instance.tanggal_kedaluwarsa.strftime('%Y-%m-%d')

    def clean(self):
        cleaned     = super().clean()
        berlaku     = cleaned.get('tanggal_berlaku')
        kedaluwarsa = cleaned.get('tanggal_kedaluwarsa')
        if berlaku and kedaluwarsa and kedaluwarsa <= berlaku:
            raise forms.ValidationError('Tanggal kedaluwarsa harus setelah tanggal berlaku.')
        return cleaned
