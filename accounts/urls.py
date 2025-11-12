from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views
from .admin_views import admin_dashboard
from .forms import CustomSetPasswordForm

app_name = 'accounts'

urlpatterns = [
    # Autenticación
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('activar/', views.activar_cuenta, name='activar'),
    path('acerca-de/', views.acerca_de, name='acerca_de'),
    
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Admin personalizado
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    
    # Reset de clave de acceso
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url=reverse_lazy('accounts:password_reset_done')
         ), 
         name='password_reset'),
    
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             form_class=CustomSetPasswordForm,
             success_url=reverse_lazy('accounts:password_reset_complete')
         ), 
         name='password_reset_confirm'),
    
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]
