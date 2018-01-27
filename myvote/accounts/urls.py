from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'account'
urlpatterns = [
    path('', views.account_settings, name='overview'),
    path('view_profile/<int:user_id>', views.account_view_profile, name='view profile'),
    path('follow/<int:user_id>', views.follow_user, name='follow user'),
    path('unfollow/<int:user_id>', views.unfollow_user, name='unfollow user'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('edit_bio/', views.edit_bio, name='edit bio'),
    path('change_password/', views.change_password, name='change password'),
    path('change_email/', views.change_email, name='change email'),
    path('delete_account/', views.delete_account, name='delete account'),
]
