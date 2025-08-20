from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.user_registration, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.get_user_profile, name='profile'),
    path('profile/update/', views.update_user_profile, name='profile_update'),
    path('change-password/', views.change_password, name='change_password'),
    path('verify/<int:user_id>/', views.verify_user, name='verify_user'),
]
