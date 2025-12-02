from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Q

from applications.usuarios.models import Perfil, Estudiante
from applications.clinica.models import Paciente_Ficticio, Etapa
from applications.evaluaciones.models import Evaluacion, Respuesta_Evaluacion

# Vista para mostrar y guardar el Diagnóstico
@login_required
def vista_diagnostico(request, paciente_id):
    paciente = get_object_or_404(Paciente_Ficticio, id=paciente_id)
    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)
    
    # CORRECCIÓN 1: Filtramos estrictamente por 'en_curso'. 
    # Si hay una antigua 'abandonada' o 'finalizada', NO la traemos.
    # Esto asegura que el campo aparezca en blanco si es un intento nuevo.
    evaluacion = Evaluacion.objects.filter(
        estudiante=estudiante, 
        paciente=paciente
    ).exclude(estado='abandonada').order_by('-id').first()

    # Si por alguna razón no hay evaluación activa (ej. acceso directo por URL),
    # redirigimos al inicio para que se cree una.
    if not evaluacion:
        return redirect('iniciar_evaluacion', paciente_id=paciente.id)

    return render(request, 'evaluaciones/diagnostico.html', {
        'paciente': paciente,
        'evaluacion': evaluacion
    })

# Vista para procesar el Resumen Final (y guardar diagnóstico por AJAX/POST)
from django.utils.dateparse import parse_datetime # <--- AGREGA ESTE IMPORT AL INICIO
# ... tus otros imports (render, timezone, etc) ...

@login_required
def resumen_evaluacion(request, paciente_id):
    paciente = get_object_or_404(Paciente_Ficticio, id=paciente_id)
    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)

    # 1. Buscar evaluación (En curso o la última finalizada para ver)
    evaluacion = Evaluacion.objects.filter(
        estudiante=estudiante, 
        paciente=paciente, 
        estado='en_curso'
    ).first()

    if not evaluacion:
        evaluacion = Evaluacion.objects.filter(
            estudiante=estudiante, 
            paciente=paciente, 
            estado='finalizada'
        ).last()

    if not evaluacion:
         return redirect('iniciar_evaluacion', paciente_id=paciente.id)

    # 2. CALCULAR Y GUARDAR TIEMPO (Pero mantener 'en_curso')
    if evaluacion.estado == 'en_curso':
        inicio_str = request.session.get('inicio_evaluacion')
        if inicio_str:
            inicio_dt = parse_datetime(inicio_str)
            if inicio_dt:
                ahora = timezone.now()
                duracion = ahora - inicio_dt
                evaluacion.tiempo_total = duracion
                # Guardamos el tiempo actualizado, pero NO finalizamos estado
                evaluacion.save()

    # Guardar diagnóstico si viene por POST (auto-save o edición)
    if request.method == 'POST':
        diagnostico_texto = request.POST.get('diagnostico')
        if diagnostico_texto:
            evaluacion.diagnostico = diagnostico_texto
            evaluacion.save()
            
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})

    # 3. CÁLCULO DE RESULTADOS (Tu lógica de contadores sigue igual)
    respuestas = Respuesta_Evaluacion.objects.filter(evaluacion=evaluacion)
    total_intentos = respuestas.count()
    correctas = respuestas.filter(correcta=True).count()
    incorrectas = total_intentos - correctas
    precision = (correctas / total_intentos * 100) if total_intentos > 0 else 0

    etapas_ids = respuestas.values_list('etapa', flat=True).distinct()
    etapas_db = Etapa.objects.filter(id__in=etapas_ids)
    
    desglose_etapas = []
    for etapa in etapas_db:
        resps_etapa = respuestas.filter(etapa=etapa)
        aciertos_etapa = resps_etapa.filter(correcta=True).count()
        intentos_etapa = resps_etapa.count()
        
        estado_etapa = "Logrado" if aciertos_etapa > 0 else "Pendiente"
        css_class = "success" if aciertos_etapa > 0 else "danger"

        desglose_etapas.append({
            'nombre': etapa.nombre,
            'intentos': intentos_etapa,
            'aciertos': aciertos_etapa,
            'estado': estado_etapa,
            'css': css_class
        })

    return render(request, 'evaluaciones/resumen.html', {
        'paciente': paciente,
        'evaluacion': evaluacion,
        'total_intentos': total_intentos,
        'correctas': correctas,
        'incorrectas': incorrectas,
        'precision': round(precision, 1),
        'desglose_etapas': desglose_etapas
    })