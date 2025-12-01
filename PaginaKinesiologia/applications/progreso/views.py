from django.shortcuts import render

# Create your views here.


from django.shortcuts import render
from applications.usuarios.models import Perfil, Estudiante
from applications.evaluaciones.models import Evaluacion, Respuesta_Evaluacion
from applications.cursos.models import Curso
from applications.clinica.models import Caso

def ver_progreso(request):
    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)
    
    # 1. Obtener evaluaciones finalizadas
    evaluaciones_qs = Evaluacion.objects.filter(estudiante=estudiante, estado='finalizada').order_by('-fecha_evaluacion')

    # --- FILTROS ---
    curso_id = request.GET.get('curso')
    caso_titulo = request.GET.get('tipo_caso')

    if curso_id:
        evaluaciones_qs = evaluaciones_qs.filter(paciente__caso__curso_id=curso_id)
    
    if caso_titulo:
        evaluaciones_qs = evaluaciones_qs.filter(paciente__caso__titulo=caso_titulo)

    # 2. Procesar datos para el template (Calcular puntajes parciales)
    reporte = []
    
    for ev in evaluaciones_qs:
        respuestas = Respuesta_Evaluacion.objects.filter(evaluacion=ev)
        
        # Contadores por etapa
        r_motivo = respuestas.filter(etapa__nombre__icontains='motivo')
        r_sintomas = respuestas.filter(etapa__nombre__icontains='sintomas')
        r_examen = respuestas.filter(etapa__nombre__icontains='examen')

        # Estructura de datos para esa evaluación
        item = {
            'evaluacion': ev,
            'paciente': ev.paciente,
            'curso': ev.paciente.caso.curso.nombre,
            'caso': ev.paciente.caso.titulo,
            
            # Puntajes formateados "X/Y"
            'score_motivo': f"{r_motivo.filter(correcta=True).count()}/{r_motivo.count()}",
            'score_sintomas': f"{r_sintomas.filter(correcta=True).count()}/{r_sintomas.count()}",
            'score_examen': f"{r_examen.filter(correcta=True).count()}/{r_examen.count()}",
            
            # Totales numéricos
            'total_correctas': respuestas.filter(correcta=True).count(),
            'total_preguntas': respuestas.count(),
            
            # Diagnóstico Docente
            'nota_docente': ev.puntaje_diagnostico if ev.puntaje_diagnostico is not None else "Pendiente",
            'comentario': ev.comentario_docente if ev.comentario_docente else "Pendiente de revisión"
        }
        reporte.append(item)

    # 3. Datos para los selectores de filtro
    # Obtenemos solo los cursos y casos en los que el estudiante ha participado
    mis_cursos_ids = evaluaciones_qs.values_list('paciente__caso__curso__id', flat=True).distinct()
    cursos_filtro = Curso.objects.filter(id__in=mis_cursos_ids)
    tipos_caso_filtro = Caso.objects.filter(curso__id__in=mis_cursos_ids).values_list('titulo', flat=True).distinct()

    return render(request, 'progreso/historial.html', {
        'reporte': reporte,
        'cursos_filtro': cursos_filtro,
        'tipos_caso_filtro': tipos_caso_filtro,
    })