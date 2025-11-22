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
                return redirect('/inicio/')
        else:
            return render(request, 'usuarios/login.html', {'error': 'Credenciales inválidas'})

    return render(request, 'usuarios/login.html')

def redireccion_inicio(request):
    return redirect('login')  # o 'inicio_estudiante' si ya está logueado



from django.contrib.auth.models import User
from applications.usuarios.models import Perfil
from django.contrib.auth.hashers import make_password

def registro_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email'].lower()
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        if User.objects.filter(username=username).exists():
            return render(request, 'usuarios/registro.html', {'error': 'Nombre de usuario ya existe'})
        if User.objects.filter(email=email).exists():
            return render(request, 'usuarios/registro.html', {'error': 'Correo ya registrado'})

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

        perfil = Perfil.objects.create(user=user, rol=rol)

        # Crear Estudiante o Docente según rol
        if rol == 'estudiante':
            from applications.usuarios.models import Estudiante
            Estudiante.objects.create(perfil=perfil)
            return redirect('/usuarios/login/')
        else:
            from applications.usuarios.models import Docente
            Docente.objects.create(perfil=perfil)
            return redirect('/usuarios/login/')

    return render(request, 'usuarios/registro.html')



from applications.usuarios.models import Estudiante
from applications.cursos.models import Curso
from applications.inscripciones.models import Solicitud_Inscripcion

def inicio_estudiante(request):
    estudiante = Estudiante.objects.get(perfil__user=request.user)
    solicitudes = Solicitud_Inscripcion.objects.filter(estudiante=estudiante, estado='aceptada')
    cursos_inscritos = [s.curso for s in solicitudes]

    return render(request, 'usuarios/inicio.html', {
        'estudiante': estudiante,
        'cursos_inscritos': cursos_inscritos
    })
