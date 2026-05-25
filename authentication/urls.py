from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # ─── Auth ───
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # ─── OTP ───
    path('otp/setup/', views.OTPSetupView.as_view(), name='otp_setup'),
    path('otp/verify/', views.OTPVerifyView.as_view(), name='otp_verify'),

    # ─── Dashboard ───
    path('dashboard/', views.DashboardRedirectView.as_view(), name='dashboard'),
    path('dashboard/admin/', views.DashboardAdminView.as_view(), name='dashboard_admin'),
    path('dashboard/hrd/', views.DashboardHRDView.as_view(), name='dashboard_hrd'),
    path('dashboard/staff/', views.DashboardStaffView.as_view(), name='dashboard_staff'),

    # ─── Profile & Password ───
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change_password'),

    # ─── User Management (Admin only) ───
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:pk>/reset-otp/', views.UserResetOTPView.as_view(), name='user_reset_otp'),
]