from django.urls import path
from . import views

urlpatterns = [
    path('inicio', views.vistaInicio.as_view(),name='inicio' ),
]