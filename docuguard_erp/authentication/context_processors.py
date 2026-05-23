"""
authentication/context_processors.py

Inject informasi user ke semua template secara otomatis.
Anggota lain bisa langsung pakai variabel ini di template mereka
tanpa perlu kirim manual dari view.

Aktifkan di settings.py → TEMPLATES → context_processors:
'authentication.context_processors.auth_context',
"""


def auth_context(request):
    """
    Context global yang tersedia di SEMUA template.

    Variabel yang tersedia:
    - {{ otp_verified }}   → True/False
    - {{ user_role }}      → 'admin' / 'hrd' / 'staff'
    - {{ is_admin }}       → True/False
    - {{ is_hrd }}         → True/False
    - {{ is_staff_user }}  → True/False
    """
    context = {
        'otp_verified': False,
        'user_role': None,
        'is_admin': False,
        'is_hrd': False,
        'is_staff_user': False,
    }

    if request.user.is_authenticated:
        context['otp_verified'] = request.session.get('otp_verified', False)
        context['user_role'] = request.user.role
        context['is_admin'] = request.user.is_admin_role
        context['is_hrd'] = request.user.is_hrd_role
        context['is_staff_user'] = request.user.is_staff_role

    return context
