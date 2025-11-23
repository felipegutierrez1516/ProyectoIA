from django.urls import path
from .views import vista_diagnostico

urlpatterns = [
    path('evaluar/<int:paciente_id>/diagnostico/', vista_diagnostico, name='diagnostico'),
]
