from django.shortcuts import render

# Create your views here.

from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from applications.usuarios.models import Perfil

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            perfil = Perfil.objects.get(user=user)

            if perfil.rol == 'docente':
                return redirect('/admin/')
            elif perfil.rol == 'estudiante':
                return redirect('inicio_estudiante')
        else:
            return render(request, 'usuarios/login.html', {'error': 'Credenciales inválidas'})

    return render(request, 'usuarios/login.html')

def redireccion_inicio(request):
    return redirect('login')  # o 'inicio_estudiante' si ya está logueado




from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from applications.usuarios.models import Perfil, Estudiante, Docente

def registro_view(request):
    if request.method == 'POST':
        password = request.POST['password']
        email = request.POST['email'].lower()
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = email  # Usar el correo como nombre de usuario
        
        # Validaciones previas
        if User.objects.filter(username=username).exists():
            return render(request, 'usuarios/registro.html', {'error': 'Este correo ya está registrado.'})

        # Crear usuario
        user = User.objects.create(
            username=username,
            password=make_password(password),
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        # Asignar rol según dominio del correo
        if email.endswith('@alumnos.ucn.cl'):
            rol = 'estudiante'
        elif email.endswith('@ucn.cl'):
            rol = 'docente'
        else:
            rol = 'estudiante'

        # Verificar si ya existe perfil
        perfil, creado = Perfil.objects.get_or_create(user=user, defaults={'rol': rol})

        # Crear Estudiante o Docente si no existen
        if rol == 'estudiante':
            Estudiante.objects.get_or_create(perfil=perfil)
        else:
            Docente.objects.get_or_create(perfil=perfil)

        return redirect('login')

    return render(request, 'usuarios/registro.html')




from applications.usuarios.models import Estudiante
from applications.cursos.models import Curso
from applications.inscripciones.models import Solicitud_Inscripcion
from applications.clinica.models import Caso  # Asegúrate de tener esta importación

def inicio_estudiante(request):
    estudiante = Estudiante.objects.get(perfil__user=request.user)
    solicitudes = Solicitud_Inscripcion.objects.filter(estudiante=estudiante, estado='aceptada')
    cursos_inscritos = [s.curso for s in solicitudes]

    casos = Caso.objects.filter(curso__in=cursos_inscritos, estado='Activo') if cursos_inscritos else []

    return render(request, 'usuarios/inicio.html', {
        'estudiante': estudiante,
        'cursos_inscritos': cursos_inscritos,
        'casos': casos
    })
