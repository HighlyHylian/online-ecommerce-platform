from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .LatestFeed import LatestFeed 


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
    path('seller/update-quantity/<int:product_id>/', views.update_quantity, name='update_quantity'),
    path('search/', views.product_search, name='product_search'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.buyer_orders, name='buyer_orders'),
    path('seller/orders/', views.seller_orders, name='seller_orders'),
    path('seller/edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('seller/payout/', views.seller_payout, name='seller_payout'),
    path('refund/<int:order_item_id>/', views.request_refund, name='request_refund'),
    path('refund/handle/<int:refund_id>/<str:action>/', views.handle_refund, name='handle_refund'),



    #path('review/<int:order_item_id>/', views.leave_review, name='leave_review'),
    path('review/<int:product_id>/', views.leave_review, name='leave_review'),




    path('seller/refunds/', views.seller_refunds, name='seller_refunds'),
    path('seller/products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('toggle-ban/<int:user_id>/', views.toggle_ban, name='toggle_ban'),
    path('rss/', LatestFeed(), name='rss-feed'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)