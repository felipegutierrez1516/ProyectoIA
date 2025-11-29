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
def resumen_evaluacion(request, paciente_id):
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
