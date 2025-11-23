from django.urls import path
from .views import ver_casos
from .views import detalle_caso
from .views import sala_espera
from .views import evaluar_paciente
from .views import preguntas_motivo
from .views import etapa_sintomas
from .views import preguntas_sintomas
from .views import examen_fisico

urlpatterns = [
    path('curso/<int:curso_id>/casos/', ver_casos, name='ver_casos'),
    path('caso/<int:caso_id>/', detalle_caso, name='detalle_caso'),
    path('caso/<int:caso_id>/sala/', sala_espera, name='sala_espera'),
    path('evaluar/<int:paciente_id>/', evaluar_paciente, name='evaluar_paciente'),
    path('evaluar/<int:paciente_id>/preguntas/motivo/', preguntas_motivo, name='preguntas_motivo'),
    path('evaluar/<int:paciente_id>/sintomas/', etapa_sintomas, name='etapa_sintomas'),
    path('evaluar/<int:paciente_id>/preguntas/sintomas/', preguntas_sintomas, name='preguntas_sintomas'),
    path('evaluar/<int:paciente_id>/examen/', examen_fisico, name='examen_fisico'),
]
