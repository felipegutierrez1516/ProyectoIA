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
    paciente = get_object_or_404(Paciente_Ficticio, id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='motivo de consulta').first()

    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)

    # 1. Crear o recuperar evaluación
    evaluacion, created = Evaluacion.objects.get_or_create(
        estudiante=estudiante,
        paciente=paciente,
        defaults={
            'nombre': f"Evaluación de {paciente.nombre}",
            'descripcion': f"Evaluación clínica para {paciente.nombre}",
            'fecha_evaluacion': timezone.now().date(),
            'diagnostico': '',
            'tiempo_total': timezone.timedelta(0),
        }
    )

    # 2. Reiniciar reloj SIEMPRE al entrar aquí (Inicio del flujo)
    request.session['inicio_evaluacion'] = timezone.now().isoformat()
    
    # Opcional: Limpiar respuestas previas si quieres que empiece de cero real
    Respuesta_Evaluacion.objects.filter(evaluacion=evaluacion).delete()

    return render(request, 'clinica/motivo_consulta.html', {
        'paciente': paciente,
        'etapa': etapa
    })

# Preguntas Motivo (Solo Lectura - El guardado es por AJAX)
def preguntas_motivo(request, paciente_id):
    paciente = get_object_or_404(Paciente_Ficticio, id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='motivo de consulta').first()
    preguntas = Tema_Interrogacion.objects.filter(etapa=etapa) if etapa else []
    
    # Calculamos cuántas correctas hay para el JS
    preguntas_correctas_count = preguntas.filter(es_correcta=True).count()

    return render(request, 'clinica/preguntas_motivo.html', {
        'paciente': paciente,
        'etapa': etapa,
        'preguntas': preguntas,
        'preguntas_correctas_count': preguntas_correctas_count
    })

# Etapa Síntomas (Video)
def etapa_sintomas(request, paciente_id):
    paciente = get_object_or_404(Paciente_Ficticio, id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='síntomas').first()

    video_id = None
    if etapa and etapa.video:
        if 'watch?v=' in etapa.video:
            video_id = etapa.video.split('watch?v=')[-1]
        elif 'youtu.be/' in etapa.video:
            video_id = etapa.video.split('youtu.be/')[-1]

    return render(request, 'clinica/etapa_sintomas.html', {
        'paciente': paciente,
        'etapa': etapa,
        'video_id': video_id
    })

# Preguntas Síntomas (Solo Lectura)
def preguntas_sintomas(request, paciente_id):
    paciente = get_object_or_404(Paciente_Ficticio, id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='síntomas').first()
    preguntas = Tema_Interrogacion.objects.filter(etapa=etapa) if etapa else []
    
    preguntas_correctas_count = preguntas.filter(es_correcta=True).count()

    return render(request, 'clinica/preguntas_sintomas.html', {
        'paciente': paciente,
        'etapa': etapa,
        'preguntas': preguntas,
        'preguntas_correctas_count': preguntas_correctas_count
    })

# Examen Físico
def examen_fisico(request, paciente_id):
    paciente = get_object_or_404(Paciente_Ficticio, id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='examen físico').first()
    
    # --- LÓGICA DE PORCENTAJES PARA PUNTOS INTERACTIVOS ---
    # Usamos COORDS_MAP del modelo para generar la lista 'partes'
    # Asumiendo que COORDS_MAP ya tiene valores en porcentaje (0-100)
    
    # Recuperamos partes guardadas en BD si existen, o usamos el mapa base
    partes_bd = Partes_del_Cuerpo.objects.filter(etapa=etapa)
    
    # Si no hay partes en BD, usamos el mapa estático para dibujar (opcional)
    # Pero lo ideal es que uses 'partes_bd' si ya llenaste la BD con el script JS.
    
    return render(request, 'clinica/examen_fisico.html', {
        'paciente': paciente,
        'etapa': etapa,
        'partes': partes_bd # Enviamos las partes desde la BD
    })

# --- API AJAX PARA GUARDAR RESPUESTAS (La solución a tus problemas) ---

# ... imports ...

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
            
            evaluacion = Evaluacion.objects.filter(estudiante=estudiante, paciente=paciente).first()
            if not evaluacion:
                return JsonResponse({'status': 'error', 'message': 'No hay evaluación iniciada'}, status=400)

            # -------------------------------------------------------------------------
            # 1. IDENTIFICAR LA ETAPA ACTUAL
            # -------------------------------------------------------------------------
            etapa_actual = None
            if pregunta_id:
                tema = Tema_Interrogacion.objects.get(id=pregunta_id)
                etapa_actual = tema.etapa
            elif nombre_parte:
                # Ajusta el filtro según cómo nombras tus etapas en BD ('examen físico', 'Examen Fisico', etc.)
                etapa_actual = Etapa.objects.filter(paciente=paciente, nombre__icontains='examen').first()

            # -------------------------------------------------------------------------
            # 2. EL CANDADO: ¿YA APROBÓ ESTA ETAPA?
            # -------------------------------------------------------------------------
            if etapa_actual:
                ya_gano = Respuesta_Evaluacion.objects.filter(
                    evaluacion=evaluacion,
                    etapa=etapa_actual,
                    correcta=True
                ).exists()

                # SI YA ACERTÓ ANTES, NO GUARDAMOS NADA MÁS (Ni correcto ni incorrecto)
                # Esto congela el contador del resumen en el momento del éxito.
                if ya_gano:
                    return JsonResponse({'status': 'ignored', 'message': 'Etapa ya finalizada exitosamente'})

            # -------------------------------------------------------------------------
            # 3. GUARDAR LA RESPUESTA (Si no había ganado aún)
            # -------------------------------------------------------------------------
            
            # CASO A: Preguntas
            if pregunta_id:
                tema = Tema_Interrogacion.objects.get(id=pregunta_id)
                
                # Evitar guardar doble click en la MISMA pregunta incorrecta
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

            # CASO B: Examen Físico
            elif nombre_parte:
                # Obtenemos la parte para guardar el nombre bonito
                parte = Partes_del_Cuerpo.objects.filter(etapa=etapa_actual, nombre=nombre_parte).first()
                display_name = parte.get_nombre_display() if parte else nombre_parte

                # Evitar guardar doble click en la MISMA zona ya evaluada
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