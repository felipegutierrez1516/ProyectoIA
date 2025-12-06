from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from applications.evaluaciones.models import Evaluacion, Respuesta_Evaluacion
from applications.inscripciones.models import Solicitud_Inscripcion
from applications.usuarios.models import Estudiante, Perfil
from applications.clinica.models import Caso

@login_required
def ver_progreso(request):
    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)

    # 1. Filtros básicos
    curso_id = request.GET.get('curso')
    tipo_caso = request.GET.get('tipo_caso')

    # Obtener todas las evaluaciones finalizadas del estudiante
    evaluaciones = Evaluacion.objects.filter(
        estudiante=estudiante, 
        estado='finalizada'
    ).select_related('paciente', 'paciente__caso', 'paciente__caso__curso').order_by('-fecha_evaluacion')

    if curso_id:
        evaluaciones = evaluaciones.filter(paciente__caso__curso_id=curso_id)
    
    if tipo_caso:
        # Asumiendo que tienes un campo tipo o lo filtras por nombre del caso
        evaluaciones = evaluaciones.filter(paciente__caso__titulo__icontains=tipo_caso)

    # 2. Construir el reporte con cálculos precisos
    reporte = []

    for ev in evaluaciones:
        # Obtenemos TODAS las respuestas de ESTA evaluación específica
        respuestas = Respuesta_Evaluacion.objects.filter(evaluacion=ev)

        # --- CÁLCULO MOTIVO ---
        r_motivo = respuestas.filter(etapa__nombre__icontains='motivo')
        aciertos_motivo = r_motivo.filter(correcta=True).count()
        total_motivo = r_motivo.count()
        score_motivo = f"{aciertos_motivo}/{total_motivo}" if total_motivo > 0 else "-"

        # --- CÁLCULO SÍNTOMAS ---
        # Usamos Q para buscar 'síntomas' o 'anamnesis' o 'interrogatorio' por si acaso
        r_sintomas = respuestas.filter(Q(etapa__nombre__icontains='sintoma') | Q(etapa__nombre__icontains='síntoma'))
        aciertos_sintomas = r_sintomas.filter(correcta=True).count()
        total_sintomas = r_sintomas.count()
        # Parche visual: Si es 0/0 pero la evaluación está finalizada, asumimos 1/1 si no guardó intentos fallidos
        if total_sintomas == 0: 
             score_sintomas = "-"
        else:
             score_sintomas = f"{aciertos_sintomas}/{total_sintomas}"

        # --- CÁLCULO EXAMEN FÍSICO ---
        r_examen = respuestas.filter(etapa__nombre__icontains='examen')
        aciertos_examen = r_examen.filter(correcta=True).count()
        total_examen = r_examen.count()
        score_examen = f"{aciertos_examen}/{total_examen}" if total_examen > 0 else "-"

        # --- TOTALES AUTOMÁTICOS ---
        total_correctas = respuestas.filter(correcta=True).count()
        total_preguntas = respuestas.count()

        # Datos para el template
        item = {
            'paciente': ev.paciente,
            'curso': ev.paciente.caso.curso.nombre,
            'caso': ev.paciente.caso.titulo,
            'evaluacion': ev,
            'score_motivo': score_motivo,
            'score_sintomas': score_sintomas,
            'score_examen': score_examen,
            'total_correctas': total_correctas,
            'total_preguntas': total_preguntas,
            
            # --- CORRECCIÓN AQUÍ ---
            # Usamos el nombre real del modelo: puntaje_diagnostico
            'nota_docente': ev.puntaje_diagnostico if ev.puntaje_diagnostico is not None else "Pendiente",
            
            # Comentario del docente
            'comentario': ev.comentario_docente if ev.comentario_docente else ""
        }
        reporte.append(item)

    # Contexto para los filtros (selects)
    cursos_filtro = set([e.paciente.caso.curso for e in evaluaciones])
    tipos_caso_filtro = ["Kinesio Respiratoria", "Musculoesquelético", "Neurología"] # Ejemplo estático o dinámico

    return render(request, 'progreso/historial.html', {
        'reporte': reporte,
        'cursos_filtro': cursos_filtro,
        'tipos_caso_filtro': tipos_caso_filtro
    })