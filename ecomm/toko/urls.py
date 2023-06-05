from django.urls import path
from . import views

app_name = 'toko'

urlpatterns = [
     path('', views.HomeListView.as_view(), name='home-produk-list'),
     path('product/<slug>/', views.ProductDetailView.as_view(), name='produk-detail'),
     path('checkout/', views.CheckoutView.as_view(), name='checkout'),
     path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
     path('remove_from_cart/<slug>/', views.remove_from_cart, name='remove-from-cart'),
     path('order-summary/', views.OrderSummaryView.as_view(), name='order-summary'),
     path('payment/<payment_method>', views.PaymentView.as_view(), name='payment'),
     path('paypal-return/', views.paypal_return, name='paypal-return'),
     path('paypal-cancel/', views.paypal_cancel, name='paypal-cancel'),
     path('filter_products/', views.filter_products, name='filter_products'),
     path('search/', views.pencarian_barang, name='pencarian_barang'),
     path('update_quantity/', views.update_quantity, name='update_quantity'),
     path('reduce_from_cart/<slug>/', views.reduce_from_cart, name='reduce-from-cart'),
     path('contact/', views.ContactView.as_view(), name='contact'),
     path('cari_produk/<str:kategori>/', views.cari_produk, name='cari_produk'),
     # path('update-add-cart/<slug>/', views.update_cart, name='update-add-cart'),
]
