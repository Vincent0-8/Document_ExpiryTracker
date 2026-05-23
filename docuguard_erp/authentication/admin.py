from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'get_full_name', 'role', 'is_otp_enabled', 'is_active', 'date_joined')
    list_filter = ('role', 'is_otp_enabled', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    # Tambahkan field role & OTP di form admin
    fieldsets = UserAdmin.fieldsets + (
        ('Info Tambahan', {
            'fields': ('role', 'phone_number', 'is_otp_enabled', 'otp_secret')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Info Tambahan', {
            'fields': ('role', 'phone_number', 'email', 'first_name', 'last_name')
        }),
    )
