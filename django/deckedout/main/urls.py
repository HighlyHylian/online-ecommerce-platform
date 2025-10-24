from django.urls import path
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('seller/add-product/', views.add_product, name='add_product'),
    path('admin/approve-products/', views.approve_products, name='approve_products'),
    path('admin-approve/', views.admin_approve, name='admin_approve'),
    path('seller/products/', views.seller_products, name='seller_products'),
    path('seller/products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('seller/orders', views.seller_orders, name='seller_orders')
    


    
    


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)