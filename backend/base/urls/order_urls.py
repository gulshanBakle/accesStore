from django.urls import path
from base.views import order_views as views


urlpatterns = [
    path('add/', views.addOrder, name='add-order'),
]
