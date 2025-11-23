from django.shortcuts import render

# Create your views here.

from applications.cursos.models import Curso
from applications.clinica.models import Caso  # si tienes un modelo llamado Caso

def ver_casos(request, curso_id):
    curso = Curso.objects.get(id=curso_id)
    casos = Caso.objects.filter(curso=curso, estado='Activo')
    return render(request, 'clinica/ver_casos.html', {
        'curso': curso,
        'casos': casos
    })




def detalle_caso(request, caso_id):
    caso = Caso.objects.get(id=caso_id)
    return render(request, 'clinica/detalle_caso.html', {'caso': caso})




from applications.clinica.models import Paciente_Ficticio

def sala_espera(request, caso_id):
    caso = Caso.objects.get(id=caso_id)
    pacientes = Paciente_Ficticio.objects.filter(caso=caso)[:5]

    casos = Caso.objects.filter(curso=caso.curso, estado='Activo')

    return render(request, 'clinica/sala_espera.html', {
        'caso': caso,
        'pacientes': pacientes,
        'casos': casos 
    })




from applications.clinica.models import Etapa

def evaluar_paciente(request, paciente_id):
    paciente = Paciente_Ficticio.objects.get(id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='motivo de consulta').first()

    return render(request, 'clinica/evaluar_paciente.html', {
        'paciente': paciente,
        'etapa': etapa
    })




from applications.clinica.models import Tema_Interrogacion

def preguntas_motivo(request, paciente_id):
    paciente = Paciente_Ficticio.objects.get(id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='motivo de consulta').first()

    preguntas = Tema_Interrogacion.objects.filter(etapa=etapa) if etapa else []

    return render(request, 'clinica/preguntas_motivo.html', {
        'paciente': paciente,
        'etapa': etapa,
        'preguntas': preguntas
    })




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




def preguntas_sintomas(request, paciente_id):
    paciente = Paciente_Ficticio.objects.get(id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='síntomas').first()

    preguntas = Tema_Interrogacion.objects.filter(etapa=etapa) if etapa else []

    return render(request, 'clinica/preguntas_sintomas.html', {
        'paciente': paciente,
        'etapa': etapa,
        'preguntas': preguntas
    })




from django.utils import timezone
from applications.clinica.models import Partes_del_Cuerpo

def examen_fisico(request, paciente_id):
    paciente = Paciente_Ficticio.objects.get(id=paciente_id)
    etapa = Etapa.objects.filter(paciente=paciente, nombre__icontains='examen físico').first()
    partes = Partes_del_Cuerpo.objects.filter(etapa=etapa) if etapa else []

    request.session['inicio_evaluacion'] = timezone.now().isoformat()

    return render(request, 'clinica/examen_fisico.html', {
        'paciente': paciente,
        'etapa': etapa,
        'partes': partes
    })
