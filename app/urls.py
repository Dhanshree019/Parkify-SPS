from django import views
from django.urls import path
from .views import *
from payment.views import *


urlpatterns = [
    path('', homepage, name='homepage'),
    path('home', homepage, name='home'),
    path('license-detection/<str:id>/', license_detection, name='license_detection'),
    path('demo',demo,name='demo'),
    path('admin/detect',demo,name='demo'),
    path('vacant-slot', VacantSlot,name='vacant-slot'),
    path('signIn', register, name='signIn'),
    path('register/', Register, name='register'),
    path('login/', Login, name='login'),
    path('logout/', Logout, name='logout'),
    path('profile', Profile, name='profile'),
    path('admin/<str:pno>', AdminView, name='admin'),
    path('payment_status/', PaymentStatus, name='payment_status'),

    path('payment_method/<str:action>', AddRemovePaymentMethod, name='payment_method'),
    path('payment/<str:action>', HandlePayment, name='payment'),

]

