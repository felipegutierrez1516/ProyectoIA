from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import login_view
from .views import registro_view
from .views import inicio_estudiante
from .views import ver_perfil

urlpatterns = [
    path('login/', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('inicio/', inicio_estudiante, name='inicio_estudiante'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('perfil/', ver_perfil, name='ver_perfil'),
]