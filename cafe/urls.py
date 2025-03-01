from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, order_list, add_order, edit_order, delete_order, calculate_revenue, index


router = DefaultRouter()
router.register(r'orders', OrderViewSet)


urlpatterns = [
    path('', index, name='index'),
    path('api/', include(router.urls)),
    path('manager/', order_list, name='order_list'),
    path('manager/add/', add_order, name='add_order'),
    path('manager/edit/<int:order_id>/', edit_order, name='edit_order'),
    path('manager/delete/<int:order_id>/', delete_order, name='delete_order'),
    path('manager/revenue/', calculate_revenue, name='calculate_revenue'),
]