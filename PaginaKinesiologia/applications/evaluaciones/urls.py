from django.urls import path
from .views import vista_diagnostico
from .views import resumen_evaluacion

urlpatterns = [
    path('evaluar/<int:paciente_id>/diagnostico/', vista_diagnostico, name='diagnostico'),
    path('evaluar/<int:paciente_id>/resumen/', resumen_evaluacion, name='resumen'),
]
