from django.urls import path
from . import views

urlpatterns = [
    path('historial/', views.ver_progreso, name='ver_progreso'),
]
