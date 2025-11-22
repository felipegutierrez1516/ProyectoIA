from django.urls import path
from .views import login_view
from .views import registro_view
from .views import inicio_estudiante

urlpatterns = [
    path('login/', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('inicio/', inicio_estudiante, name='inicio_estudiante'),
]