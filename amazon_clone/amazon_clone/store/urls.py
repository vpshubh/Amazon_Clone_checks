# Store App URLs (store/urls.py)

from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    # Add more URL patterns as needed
    # path('product/<int:pk>/', views.product_detail, name='product_detail'),
    # path('cart/', views.cart, name='cart'),
    # path('checkout/', views.checkout, name='checkout'),
]