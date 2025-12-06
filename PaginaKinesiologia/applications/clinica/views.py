from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from applications.cursos.models import Curso
from applications.clinica.models import Caso, Paciente_Ficticio, Etapa, Tema_Interrogacion, Partes_del_Cuerpo, COORDS_MAP
from applications.usuarios.models import Perfil, Estudiante
from applications.evaluaciones.models import Evaluacion, Respuesta_Evaluacion

# Ver casos clínicos activos por curso
def ver_casos(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    casos = Caso.objects.filter(curso=curso, estado='Activo')
    return render(request, 'clinica/ver_casos.html', {
        'curso': curso,
        'casos': casos
    })

# Detalle de un caso clínico
def detalle_caso(request, caso_id):
    caso = get_object_or_404(Caso, id=caso_id)
    return render(request, 'clinica/detalle_caso.html', {'caso': caso})

# Sala de espera
def sala_espera(request, caso_id):
    caso = get_object_or_404(Caso, id=caso_id)
    pacientes = Paciente_Ficticio.objects.filter(caso=caso)[:5]
    casos = Caso.objects.filter(curso=caso.curso, estado='Activo')

    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)

    evaluaciones_realizadas = Evaluacion.objects.filter(
        estudiante=estudiante, 
        paciente__in=pacientes,
        estado='finalizada'
    ).values_list('paciente_id', flat=True)

    return render(request, 'clinica/sala_espera.html', {
        'caso': caso,
        'pacientes': pacientes,
        'casos': casos,
        'pacientes_evaluados': list(evaluaciones_realizadas)
    })

# Inicio de evaluación (Motivo Consulta)
def evaluar_paciente(request, paciente_id):
    # Esta vista renderiza el video del motivo de consulta
    paciente = get_object_or_404(Paciente_Ficticio, id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='motivo de consulta').first()
    
    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)

    # Solo buscamos la activa. Si el usuario intenta entrar aquí directamente sin pasar por
    # iniciar_evaluacion (por url directa), lo mandamos al inicio para que se cree bien.
    evaluacion = Evaluacion.objects.filter(estudiante=estudiante, paciente=paciente, estado='en_curso').first()
    
    if not evaluacion:
        return redirect('iniciar_evaluacion', paciente_id=paciente.id)

    return render(request, 'clinica/motivo_consulta.html', {
        'paciente': paciente,
        'etapa': etapa,
        'evaluacion_id': evaluacion.id
    })


# Preguntas Motivo
def preguntas_motivo(request, paciente_id):
    paciente = get_object_or_404(Paciente_Ficticio, id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='motivo de consulta').first()
    
    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)
    
    # CORRECCIÓN 2: Obtener solo la evaluación 'en_curso'
    evaluacion = Evaluacion.objects.filter(estudiante=estudiante, paciente=paciente, estado='en_curso').first()

    preguntas = Tema_Interrogacion.objects.filter(etapa=etapa) if etapa else []
    
    intentos_realizados = 0
    ya_acerto = False

    if evaluacion:
        # Recuperar historial de respuestas SOLO para esta etapa
        respuestas_db = Respuesta_Evaluacion.objects.filter(evaluacion=evaluacion, etapa=etapa)
        
        # CORRECCIÓN 5: Contar intentos reales para enviarlos al template
        intentos_realizados = respuestas_db.count()
        
        historial = {r.descripcion: r.correcta for r in respuestas_db}
        
        if respuestas_db.filter(correcta=True).exists():
            ya_acerto = True

        for p in preguntas:
            if p.pregunta in historial:
                p.respondida = True
                p.fue_correcta = historial[p.pregunta]
            else:
                p.respondida = False

    return render(request, 'clinica/preguntas_motivo.html', {
        'paciente': paciente,
        'etapa': etapa,
        'preguntas': preguntas,
        'intentos_previos': intentos_realizados, # Enviamos esto para que el JS sepa en qué número empezar (1/2, etc.)
        'ya_acerto': ya_acerto
    })

# Etapa Síntomas (Video)
def etapa_sintomas(request, paciente_id):
    paciente = get_object_or_404(Paciente_Ficticio, id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='síntomas').first()

    return render(request, 'clinica/etapa_sintomas.html', {
        'paciente': paciente,
        'etapa': etapa,
    })

# Preguntas Síntomas
def preguntas_sintomas(request, paciente_id):
    paciente = get_object_or_404(Paciente_Ficticio, id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='síntomas').first()
    
    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)
    
    # CORRECCIÓN: Filtro estricto por en_curso
    evaluacion = Evaluacion.objects.filter(estudiante=estudiante, paciente=paciente, estado='en_curso').first()

    preguntas = Tema_Interrogacion.objects.filter(etapa=etapa) if etapa else []
    
    intentos_realizados = 0
    ya_acerto = False

    if evaluacion:
        respuestas_db = Respuesta_Evaluacion.objects.filter(evaluacion=evaluacion, etapa=etapa)
        
        # CORRECCIÓN 5: Contar intentos para esta etapa
        intentos_realizados = respuestas_db.count()
        historial = {r.descripcion: r.correcta for r in respuestas_db}
        
        if respuestas_db.filter(correcta=True).exists():
            ya_acerto = True
        
        for p in preguntas:
            if p.pregunta in historial:
                p.respondida = True
                p.fue_correcta = historial[p.pregunta]
            else:
                p.respondida = False
    
    return render(request, 'clinica/preguntas_sintomas.html', {
        'paciente': paciente,
        'etapa': etapa,
        'preguntas': preguntas,
        'intentos_previos': intentos_realizados,
        'ya_acerto': ya_acerto
    })

# Examen Físico
def examen_fisico(request, paciente_id):
    paciente = get_object_or_404(Paciente_Ficticio, id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='examen físico').first()
    
    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)
    
    # CORRECCIÓN: Filtro estricto por en_curso
    evaluacion = Evaluacion.objects.filter(estudiante=estudiante, paciente=paciente, estado='en_curso').first()

    partes_base = Partes_del_Cuerpo.objects.filter(etapa=etapa)
    
    partes_visitadas_nombres = []
    intentos_realizados = 0
    ya_acerto = False

    if evaluacion and etapa:
        respuestas = Respuesta_Evaluacion.objects.filter(evaluacion=evaluacion, etapa=etapa)
        
        # CORRECCIÓN 3: Recuperar la lista de partes ya tocadas
        partes_visitadas_nombres = list(respuestas.values_list('respuesta_estudiante', flat=True))
        intentos_realizados = respuestas.count()
        
        if respuestas.filter(correcta=True).exists():
            ya_acerto = True

    return render(request, 'clinica/examen_fisico.html', {
        'paciente': paciente,
        'etapa': etapa,
        'partes': partes_base,
        'partes_visitadas': json.dumps(partes_visitadas_nombres), # Enviamos al JS como JSON
        'intentos_previos': intentos_realizados,
        'ya_acerto': ya_acerto
    })

# API AJAX
def registrar_respuesta_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            paciente_id = data.get('paciente_id')
            pregunta_id = data.get('pregunta_id') 
            nombre_parte = data.get('nombre_parte')
            es_correcta = data.get('es_correcta')

            paciente = Paciente_Ficticio.objects.get(id=paciente_id)
            perfil = Perfil.objects.get(user=request.user)
            estudiante = Estudiante.objects.get(perfil=perfil)
            
            # CORRECCIÓN CRÍTICA: Filtrar por estado='en_curso' para evitar guardar en evaluaciones viejas
            evaluacion = Evaluacion.objects.filter(estudiante=estudiante, paciente=paciente, estado='en_curso').first()
            
            if not evaluacion:
                return JsonResponse({'status': 'error', 'message': 'No hay evaluación activa'}, status=400)

            etapa_actual = None
            if pregunta_id:
                tema = Tema_Interrogacion.objects.get(id=pregunta_id)
                etapa_actual = tema.etapa
            elif nombre_parte:
                etapa_actual = Etapa.objects.filter(paciente=paciente, nombre__icontains='examen').first()

            if etapa_actual:
                ya_gano = Respuesta_Evaluacion.objects.filter(
                    evaluacion=evaluacion,
                    etapa=etapa_actual,
                    correcta=True
                ).exists()

                if ya_gano:
                    return JsonResponse({'status': 'ignored', 'message': 'Etapa ya finalizada'})

            # Guardar Pregunta
            if pregunta_id:
                tema = Tema_Interrogacion.objects.get(id=pregunta_id)
                
                # Evitar duplicados
                if Respuesta_Evaluacion.objects.filter(evaluacion=evaluacion, descripcion=tema.pregunta).exists():
                     return JsonResponse({'status': 'ignored', 'message': 'Pregunta ya respondida'})

                Respuesta_Evaluacion.objects.create(
                    evaluacion=evaluacion,
                    etapa=tema.etapa,
                    descripcion=tema.pregunta,
                    respuesta_estudiante="Seleccionada en Quiz",
                    retroalimentacion="Correcto" if es_correcta else tema.justificacion_error,
                    correcta=es_correcta,
                    puntaje_obtenido=1.0 if es_correcta else 0.0
                )

            # Guardar Examen
            elif nombre_parte:
                parte = Partes_del_Cuerpo.objects.filter(etapa=etapa_actual, nombre=nombre_parte).first()
                display_name = parte.get_nombre_display() if parte else nombre_parte

                if Respuesta_Evaluacion.objects.filter(evaluacion=evaluacion, respuesta_estudiante=nombre_parte).exists():
                    return JsonResponse({'status': 'ignored', 'message': 'Zona ya evaluada'})

                Respuesta_Evaluacion.objects.create(
                    evaluacion=evaluacion,
                    etapa=etapa_actual,
                    descripcion=f"Examen de zona: {display_name}",
                    respuesta_estudiante=nombre_parte,
                    retroalimentacion="Hallazgo positivo" if es_correcta else "Sin hallazgos",
                    correcta=es_correcta,
                    puntaje_obtenido=1.0 if es_correcta else 0.0
                )

            return JsonResponse({'status': 'ok'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'invalid method'}, status=400)



def iniciar_evaluacion(request, paciente_id):
    paciente = get_object_or_404(Paciente_Ficticio, id=paciente_id)
    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)

    # 1. Marcar como 'abandonada' cualquier evaluación previa que haya quedado 'en_curso'
    #    (Esto hace que al volver a entrar, el intento anterior se "pierda/resetee" para el usuario)
    Evaluacion.objects.filter(
        estudiante=estudiante,
        paciente=paciente,
        estado='en_curso'
    ).delete() # O puedes usar .delete() si prefieres borrar el historial basura

    # 2. Crear la NUEVA evaluación limpia
    Evaluacion.objects.create(
        estudiante=estudiante,
        paciente=paciente,
        nombre=f"Evaluación de {paciente.nombre}",
        descripcion=f"Evaluación clínica para {paciente.nombre}",
        fecha_evaluacion=timezone.now().date(),
        diagnostico='',
        tiempo_total=timezone.timedelta(0),
        estado='en_curso'
    )
    
    # 3. Reiniciar reloj
    request.session['inicio_evaluacion'] = timezone.now().isoformat()

    # 4. Redirigir al primer paso visual (Motivo de Consulta)
    return redirect('motivo_consulta', paciente_id=paciente.id)