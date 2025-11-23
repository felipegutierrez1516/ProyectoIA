from django.shortcuts import render

# Create your views here.


from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Evaluacion, Respuesta_Evaluacion, Envio_Docente
from clinica.models import Paciente_Ficticio
from usuarios.models import Estudiante, Docente

def vista_diagnostico(request, paciente_id):
    paciente = Paciente_Ficticio.objects.get(id=paciente_id)
    estudiante = request.user.estudiante  # Asegúrate de tener el estudiante logueado
    docente = paciente.docente_asignado  # Este campo debe existir en Paciente_Ficticio

    # Buscar o crear evaluación
    evaluacion, created = Evaluacion.objects.get_or_create(
        estudiante=estudiante,
        paciente=paciente,
        defaults={
            'nombre': f'Evaluación {paciente.nombre}',
            'descripcion': f'Evaluación médica de {paciente.nombre}',
            'fecha_evaluacion': timezone.now().date()
        }
    )

    # Calcular tiempo
    inicio = request.session.get('inicio_evaluacion')
    tiempo_total = timezone.now() - timezone.datetime.fromisoformat(inicio) if inicio else timezone.timedelta()

    # Contar respuestas correctas
    respuestas = Respuesta_Evaluacion.objects.filter(evaluacion=evaluacion)
    correctas = respuestas.filter(correcta=True).count()
    total = respuestas.count()

    if request.method == 'POST':
        diagnostico = request.POST.get('diagnostico')
        evaluacion.diagnostico = diagnostico
        evaluacion.tiempo_total = tiempo_total
        evaluacion.respuestas_correctas_primer_intento = correctas
        evaluacion.save()

        Envio_Docente.objects.create(
            docente=docente,
            respuesta_evaluacion=respuestas.last(),
            estudiante=estudiante,
            fecha_entrega=timezone.now().date(),
            estado_revision='pendiente'
        )

        return redirect('confirmacion_envio')  # Crea esta vista si quieres

    return render(request, 'evaluaciones/diagnostico.html', {
        'evaluacion': evaluacion,
        'paciente': paciente,
        'correctas': correctas,
        'total': total,
        'tiempo_total': tiempo_total
    })
