from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from applications.clinica.models import Paciente_Ficticio
from applications.usuarios.models import Perfil, Estudiante
from .models import Evaluacion, Respuesta_Evaluacion, Envio_Docente

# Vista del diagnóstico clínico
def vista_diagnostico(request, paciente_id):
    paciente = Paciente_Ficticio.objects.get(id=paciente_id)
    return render(request, 'evaluaciones/diagnostico.html', {
        'paciente': paciente
    })

# Vista resumen de evaluación
def resumen_evaluacion2(request, paciente_id):
    paciente = Paciente_Ficticio.objects.get(id=paciente_id)

    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)

    evaluacion = Evaluacion.objects.filter(estudiante=estudiante, paciente=paciente).first()
    respuestas = Respuesta_Evaluacion.objects.filter(evaluacion=evaluacion)

    motivo = respuestas.filter(etapa__nombre__icontains='motivo', correcta=True).count()
    sintomas = respuestas.filter(etapa__nombre__icontains='sintomas', correcta=True).count()
    examen = respuestas.filter(etapa__nombre__icontains='examen físico', correcta=True).count()
    total = respuestas.count()
    correctas = motivo + sintomas + examen

    inicio = request.session.get('inicio_evaluacion')
    tiempo_total = timezone.now() - timezone.datetime.fromisoformat(inicio) if inicio else timezone.timedelta()

    # Guardar tiempo en la evaluación si existe
    if evaluacion:
        evaluacion.tiempo_total = tiempo_total
        evaluacion.save()

    if request.method == 'POST':
        docente = getattr(getattr(getattr(paciente, 'caso', None), 'curso', None), 'docente', None)
        ultima_respuesta = respuestas.last()

        if docente and ultima_respuesta:
            Envio_Docente.objects.create(
                docente=docente,
                respuesta_evaluacion=ultima_respuesta,
                estudiante=estudiante,
                fecha_entrega=timezone.now().date(),
                estado_revision='pendiente'
            )
            messages.success(request, "Respuesta enviada con éxito")
            return redirect('inicio_estudiante')
        else:
            messages.error(request, "No se pudo enviar: faltan respuestas o vínculo con docente.")
            return redirect(request.path)

    return render(request, 'evaluaciones/resumen.html', {
        'paciente': paciente,
        'evaluacion': evaluacion,
        'motivo': motivo,
        'sintomas': sintomas,
        'examen': examen,
        'correctas': correctas,
        'total': total,
        'tiempo_total': tiempo_total
    })




# applications/evaluaciones/views.py

# applications/evaluaciones/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
import datetime # Usamos la librería nativa en lugar de dateutil

from applications.clinica.models import Paciente_Ficticio
from applications.evaluaciones.models import Evaluacion, Respuesta_Evaluacion
from applications.usuarios.models import Estudiante, Perfil

def resumen_evaluacion(request, paciente_id):
    paciente = get_object_or_404(Paciente_Ficticio, id=paciente_id)
    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)
    
    # Obtener la evaluación activa
    evaluacion = Evaluacion.objects.filter(estudiante=estudiante, paciente=paciente).first()
    
    if not evaluacion:
        return redirect('inicio_estudiante')

    # 1. Guardar Diagnóstico
    if request.method == 'POST' and 'diagnostico' in request.POST:
        evaluacion.diagnostico = request.POST.get('diagnostico')
        evaluacion.save()

    # 2. Calcular Puntajes
    respuestas = Respuesta_Evaluacion.objects.filter(evaluacion=evaluacion)
    
    score_motivo = {
        'correctas': respuestas.filter(etapa__nombre__icontains='motivo', correcta=True).count(),
        'total': respuestas.filter(etapa__nombre__icontains='motivo').count()
    }
    score_sintomas = {
        'correctas': respuestas.filter(etapa__nombre__icontains='síntomas', correcta=True).count(),
        'total': respuestas.filter(etapa__nombre__icontains='síntomas').count()
    }
    score_examen = {
        'correctas': respuestas.filter(etapa__nombre__icontains='examen', correcta=True).count(),
        'total': respuestas.filter(etapa__nombre__icontains='examen').count()
    }
    
    total_correctas = score_motivo['correctas'] + score_sintomas['correctas'] + score_examen['correctas']
    total_preguntas = score_motivo['total'] + score_sintomas['total'] + score_examen['total']
    
    # 3. Calcular Tiempo
    tiempo_formateado = "00:00:00"
    inicio_tiempo = None
    
    if 'inicio_evaluacion' in request.session:
        try:
            # CORRECCIÓN: Usamos datetime.datetime.fromisoformat (Nativo de Python)
            inicio_tiempo = datetime.datetime.fromisoformat(request.session['inicio_evaluacion'])
        except (ValueError, TypeError):
            # Si falla, usamos la fecha de la base de datos como respaldo
            inicio_tiempo = evaluacion.fecha_evaluacion

    if not inicio_tiempo:
        inicio_tiempo = timezone.now()

    fin_tiempo = timezone.now()
    
    # Calcular diferencia
    duracion = fin_tiempo - inicio_tiempo
    
    # Evitar tiempos negativos o absurdamente largos (por sesiones viejas)
    if duracion.total_seconds() < 0 or duracion.total_seconds() > 18000: # Limite de 5 horas
        duracion = datetime.timedelta(seconds=0)

    # Formateo HH:MM:SS
    total_seconds = int(duracion.total_seconds())
    horas = total_seconds // 3600
    minutos = (total_seconds % 3600) // 60
    segundos = total_seconds % 60
    tiempo_formateado = f"{horas:02}:{minutos:02}:{segundos:02}"
    
    # Guardar tiempo final
    evaluacion.tiempo_total = duracion
    evaluacion.save()

    # 4. Enviar Correo
    if request.method == 'POST' and 'enviar_correo' in request.POST:
        
        # Obtener correo del docente (Asumiendo relación: Paciente -> Caso -> Curso -> Docente)
        # Asegúrate de que tu modelo 'Curso' tenga el campo 'docente' relacionado al User o Docente
        docente_email = "correo_docente_ejemplo@ucn.cl" 
        if paciente.caso and paciente.caso.curso and hasattr(paciente.caso.curso, 'docente'):
             # Ajusta esto según cómo se llame el campo en tu modelo Curso
             # Si en Curso tienes: docente = models.ForeignKey(User...), usa:
             # docente_email = paciente.caso.curso.docente.email
             pass

        asunto = f"Resultados Evaluación: {estudiante.perfil.user.first_name} {estudiante.perfil.user.last_name} - {paciente.nombre}"
        mensaje = f"""
        Resumen de Evaluación Clínica
        -----------------------------
        Estudiante: {estudiante.perfil.user.first_name} {estudiante.perfil.user.last_name}
        Paciente: {paciente.nombre}
        Fecha: {timezone.now().strftime('%d/%m/%Y %H:%M')}
        Tiempo Total: {tiempo_formateado}

        PUNTAJES OBTENIDOS:
        - Motivo de Consulta: {score_motivo['correctas']} / {score_motivo['total']}
        - Síntomas: {score_sintomas['correctas']} / {score_sintomas['total']}
        - Examen Físico: {score_examen['correctas']} / {score_examen['total']}
        
        TOTAL GENERAL: {total_correctas} / {total_preguntas}

        DIAGNÓSTICO DEL ESTUDIANTE:
        {evaluacion.diagnostico}
        """
        
        try:
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [docente_email],
                fail_silently=False,
            )
            evaluacion.estado = 'finalizada'
            evaluacion.save()
            messages.success(request, '¡Evaluación enviada exitosamente al docente!')
            
            # Limpiar sesión
            if 'inicio_evaluacion' in request.session:
                del request.session['inicio_evaluacion']
                
            return redirect('sala_espera', caso_id=paciente.caso.id)
            
        except Exception as e:
            messages.error(request, f'Error al enviar: {e}')

    return render(request, 'evaluaciones/resumen.html', {
        'paciente': paciente,
        'evaluacion': evaluacion,
        'score_motivo': score_motivo,
        'score_sintomas': score_sintomas,
        'score_examen': score_examen,
        'total_correctas': total_correctas,
        'total_preguntas': total_preguntas,
        'tiempo_total': tiempo_formateado,
    })