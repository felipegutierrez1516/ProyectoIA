from django.shortcuts import render

# Create your views here.


from django.shortcuts import render
from applications.clinica.models import Paciente_Ficticio

def vista_diagnostico(request, paciente_id):
    paciente = Paciente_Ficticio.objects.get(id=paciente_id)
    return render(request, 'evaluaciones/diagnostico.html', {
        'paciente': paciente
    })

