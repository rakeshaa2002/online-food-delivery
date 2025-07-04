from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('place-order/', views.place_order, name='place_order'),
    path('update-cart-quantity/<int:cart_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('delete-cart-item/<int:cart_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('delete-order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('create-stripe-session/', views.create_stripe_session, name='create_stripe_session'),
    path('address/', views.address, name='address'),
    path('confirm-order/', views.confirm_order, name='confirm_order'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    # path('logout/', views.logout_view, name='logout'),
]