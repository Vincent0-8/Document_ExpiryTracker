def auth_context(request):
    """
    Context processor — inject info user ke semua template.
    Jadi di template bisa langsung pakai {{ current_user }}, {{ is_admin }}, dll.
    """
    context = {}

    if request.user.is_authenticated:
        context['current_user']  = request.user
        context['is_admin']      = request.user.is_admin_role
        context['is_hrd']        = request.user.is_hrd_role
        context['is_staff_role'] = request.user.is_staff_role
        context['user_role']     = request.user.role
        context['user_fullname'] = request.user.get_full_name() or request.user.username

    return context