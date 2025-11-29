from django.urls import path
from . import views

urlpatterns = [
    # Casos clínicos
    path('ver_casos/<int:curso_id>/', views.ver_casos, name='ver_casos'),
    path('detalle_caso/<int:caso_id>/', views.detalle_caso, name='detalle_caso'),

    # Sala de espera
    path('sala_espera/<int:caso_id>/', views.sala_espera, name='sala_espera'),

    # Evaluación clínica
    path('motivo-consulta/<int:paciente_id>/', views.evaluar_paciente, name='motivo_consulta'),

    # Motivo de consulta
    path('motivo/<int:paciente_id>/', views.preguntas_motivo, name='preguntas_motivo'),

    # Síntomas
    path('sintomas/<int:paciente_id>/', views.etapa_sintomas, name='etapa_sintomas'),
    path('preguntas_sintomas/<int:paciente_id>/', views.preguntas_sintomas, name='preguntas_sintomas'),

    # Examen físico
    path('examen_fisico/<int:paciente_id>/', views.examen_fisico, name='examen_fisico'),
    path('registrar_parte/<int:paciente_id>/', views.registrar_parte_examen_fisico, name='registrar_parte_examen_fisico'),
]

