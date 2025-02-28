from django.contrib import admin
from django.urls import path, include
from cafe import views


urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('manager/', include('cafe.urls')),
]