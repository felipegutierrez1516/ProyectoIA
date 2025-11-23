from django.shortcuts import render

# Create your views here.

from django.shortcuts import redirect
from applications.usuarios.models import Estudiante
from applications.cursos.models import Curso
from applications.inscripciones.models import Solicitud_Inscripcion




def cursos_disponibles(request):
    cursos = Curso.objects.all()
    return render(request, 'inscripciones/cursos_disponibles.html', {'cursos': cursos})




def detalle_curso(request, curso_id):
    curso = Curso.objects.get(id=curso_id)
    docente = curso.docente.perfil.user.get_full_name()
    return render(request, 'inscripciones/detalle_curso.html', {
        'curso': curso,
        'docente': docente
    })




def inscribirse(request, curso_id):
    estudiante = Estudiante.objects.get(perfil__user=request.user)
    curso = Curso.objects.get(id=curso_id)

    # Verifica si ya está inscrito
    if not Solicitud_Inscripcion.objects.filter(estudiante=estudiante, curso=curso).exists():
        Solicitud_Inscripcion.objects.create(estudiante=estudiante, curso=curso, estado='pendiente')

    return redirect('inicio_estudiante')




def cursos_disponibles(request):
    cursos = Curso.objects.filter(estado='activo')
    return render(request, 'inscripciones/cursos_disponibles.html', {'cursos': cursos})
