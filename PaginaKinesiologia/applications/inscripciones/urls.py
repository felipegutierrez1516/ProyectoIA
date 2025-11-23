from django.urls import path
from .views import cursos_disponibles, detalle_curso, inscribirse

urlpatterns = [
    path('cursos/', cursos_disponibles, name='cursos_disponibles'),
    path('curso/<int:curso_id>/', detalle_curso, name='detalle_curso'),
    path('inscribirse/<int:curso_id>/', inscribirse, name='inscribirse'),
]
