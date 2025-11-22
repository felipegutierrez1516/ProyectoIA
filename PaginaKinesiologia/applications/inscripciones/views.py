from django.shortcuts import render

# Create your views here.

from django.shortcuts import redirect
from applications.usuarios.models import Estudiante
from applications.cursos.models import Curso
from applications.inscripciones.models import Solicitud_Inscripcion

def inscribirse(request):
    estudiante = Estudiante.objects.get(perfil__user=request.user)
    curso = Curso.objects.first()  # o lógica para elegir curso
    Solicitud_Inscripcion.objects.create(estudiante=estudiante, curso=curso, estado='pendiente')
    return redirect('inicio_estudiante')
