from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import JsonResponse
from applications.cursos.models import Curso
from applications.clinica.models import Caso, Paciente_Ficticio, Etapa, Tema_Interrogacion, Partes_del_Cuerpo
from applications.usuarios.models import Perfil, Estudiante
from applications.evaluaciones.models import Evaluacion, Respuesta_Evaluacion

# Ver casos clínicos activos por curso
def ver_casos(request, curso_id):
    curso = Curso.objects.get(id=curso_id)
    casos = Caso.objects.filter(curso=curso, estado='Activo')
    return render(request, 'clinica/ver_casos.html', {
        'curso': curso,
        'casos': casos
    })

# Detalle de un caso clínico
def detalle_caso(request, caso_id):
    caso = Caso.objects.get(id=caso_id)
    return render(request, 'clinica/detalle_caso.html', {'caso': caso})

# Sala de espera con pacientes ficticios
def sala_espera(request, caso_id):
    caso = Caso.objects.get(id=caso_id)
    pacientes = Paciente_Ficticio.objects.filter(caso=caso)[:5]
    casos = Caso.objects.filter(curso=caso.curso, estado='Activo')
    return render(request, 'clinica/sala_espera.html', {
        'caso': caso,
        'pacientes': pacientes,
        'casos': casos 
    })

# Inicio de evaluación: crea evaluación y registra inicio
def evaluar_paciente(request, paciente_id):
    paciente = Paciente_Ficticio.objects.get(id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='motivo de consulta').first()

    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)

    evaluacion, _ = Evaluacion.objects.get_or_create(
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

    if 'inicio_evaluacion' not in request.session:
        request.session['inicio_evaluacion'] = timezone.now().isoformat()

    return render(request, 'clinica/motivo_consulta.html', {
        'paciente': paciente,
        'etapa': etapa
    })

# Preguntas de motivo de consulta
def preguntas_motivo(request, paciente_id):
    paciente = Paciente_Ficticio.objects.get(id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='motivo de consulta').first()
    preguntas = Tema_Interrogacion.objects.filter(etapa=etapa) if etapa else []

    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)
    evaluacion = Evaluacion.objects.filter(estudiante=estudiante, paciente=paciente).first()

    if request.method == 'POST':
        pregunta_id = request.POST.get('pregunta_id')
        respuesta_texto = request.POST.get('respuesta')
        tema = Tema_Interrogacion.objects.get(id=pregunta_id, etapa=etapa)

        es_correcta = (respuesta_texto.strip().lower() == tema.respuesta.strip().lower())
        retro = '' if es_correcta else (tema.justificacion_error or 'Respuesta incorrecta.')

        Respuesta_Evaluacion.objects.create(
            evaluacion=evaluacion,
            etapa=etapa,
            descripcion=tema.pregunta,
            respuesta_estudiante=respuesta_texto,
            retroalimentacion=retro,
            correcta=es_correcta,
            puntaje_obtenido=1.0 if es_correcta else 0.0,
        )

    return render(request, 'clinica/preguntas_motivo.html', {
        'paciente': paciente,
        'etapa': etapa,
        'preguntas': preguntas
    })

# Etapa de síntomas con video
def etapa_sintomas(request, paciente_id):
    paciente = Paciente_Ficticio.objects.get(id=paciente_id)
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

# Preguntas de síntomas
def preguntas_sintomas(request, paciente_id):
    paciente = Paciente_Ficticio.objects.get(id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='síntomas').first()
    preguntas = Tema_Interrogacion.objects.filter(etapa=etapa) if etapa else []

    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)
    evaluacion = Evaluacion.objects.filter(estudiante=estudiante, paciente=paciente).first()

    if request.method == 'POST':
        pregunta_id = request.POST.get('pregunta_id')
        respuesta_texto = request.POST.get('respuesta')
        tema = Tema_Interrogacion.objects.get(id=pregunta_id, etapa=etapa)

        es_correcta = (respuesta_texto.strip().lower() == tema.respuesta.strip().lower())
        retro = '' if es_correcta else (tema.justificacion_error or 'Respuesta incorrecta.')

        Respuesta_Evaluacion.objects.create(
            evaluacion=evaluacion,
            etapa=etapa,
            descripcion=tema.pregunta,
            respuesta_estudiante=respuesta_texto,
            retroalimentacion=retro,
            correcta=es_correcta,
            puntaje_obtenido=1.0 if es_correcta else 0.0,
        )

    return render(request, 'clinica/preguntas_sintomas.html', {
        'paciente': paciente,
        'etapa': etapa,
        'preguntas': preguntas
    })

# Examen físico y selección de partes
def examen_fisico(request, paciente_id):
    paciente = Paciente_Ficticio.objects.get(id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='examen físico').first()
    partes = Partes_del_Cuerpo.objects.filter(etapa=etapa) if etapa else []

    return render(request, 'clinica/examen_fisico.html', {
        'paciente': paciente,
        'etapa': etapa,
        'partes': partes
    })

# Registro de selección de parte del cuerpo (AJAX)
def registrar_parte_examen_fisico(request, paciente_id):
    if request.method == 'POST':
        paciente = Paciente_Ficticio.objects.get(id=paciente_id)
        perfil = Perfil.objects.get(user=request.user)
        estudiante = Estudiante.objects.get(perfil=perfil)
        evaluacion = Evaluacion.objects.filter(estudiante=estudiante, paciente=paciente).first()

        nombre_parte = request.POST.get('nombre_parte')
        etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='examen físico').first()
        parte = Partes_del_Cuerpo.objects.get(etapa=etapa, nombre=nombre_parte)

        Respuesta_Evaluacion.objects.create(
            evaluacion=evaluacion,
            etapa=etapa,
            descripcion=f"Selección de parte: {parte.get_nombre_display()}",
            respuesta_estudiante=parte.nombre,
            retroalimentacion='' if parte.correcta else 'Selección incorrecta.',
            correcta=parte.correcta,
            puntaje_obtenido=1.0 if parte.correcta else 0.0,
        )

        return JsonResponse({'ok': True})
