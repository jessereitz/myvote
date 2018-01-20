from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'account'
urlpatterns = [
    path('', views.account_overview, name='account overview'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('change_password/', views.change_password, name='change password'),
    path('change_email/', views.change_email, name='change email'),
    path('delete_account/', views.delete_account, name='delete account'),
]
