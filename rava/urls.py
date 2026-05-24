"""
URL configuration for rava project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView  # Import this
from django.contrib.auth.decorators import login_required  # Import this
from rava_app import views as rava_views

studio_view = login_required(TemplateView.as_view(template_name="studio.html"))
profile_view = login_required(TemplateView.as_view(
    template_name="account/profile.html"))

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Custom Auth Routes
    path('accounts/login/', rava_views.custom_login, name='account_login'),
    path('accounts/signup/', rava_views.custom_signup, name='account_signup'),
    path('accounts/logout/', rava_views.custom_logout, name='account_logout'),
    path('accounts/verify-otp/', rava_views.verify_otp, name='verify_otp'),
    path('accounts/refresh/', rava_views.refresh_token_endpoint, name='refresh_token'),
    
    # 1. Your new Landing Page
    path('', TemplateView.as_view(template_name="index.html"), name='home'),

    # 2. Your new Studio Page (Protected)
    path('studio/', studio_view, name='studio'),
    path('accounts/profile/', profile_view, name='account_profile'),
]
