from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('about/', views.about, name='about'),
    path('login/', views.login_view, name='login'),   
    path('signup/', views.signup_view, name='signup'),  
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile, name='user_profile'),
    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('skateboards/', views.skateboards, name='skateboards'),
    path('blog/', views.blog, name='blog'),
    path('index/', views.home, name='home'),
]
