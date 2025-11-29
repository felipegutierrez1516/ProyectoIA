from django.urls import path
from . import views

urlpatterns = [
    path('diagnostico/<int:paciente_id>/', views.vista_diagnostico, name='vista_diagnostico'),
    path('evaluar/<int:paciente_id>/resumen/', views.resumen_evaluacion, name='resumen_evaluacion'),
]

