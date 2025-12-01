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

# applications/usuarios/views.py

def inicio_estudiante(request):
    estudiante = Estudiante.objects.get(perfil__user=request.user)
    
    # Obtener todos los cursos inscritos
    solicitudes = Solicitud_Inscripcion.objects.filter(estudiante=estudiante, estado='aceptada')
    cursos_inscritos = [s.curso for s in solicitudes]

    # LÓGICA DE CURSO ACTIVO
    curso_seleccionado = None
    
    if cursos_inscritos:
        # 1. Si el estudiante eligió uno en ajustes, usamos ese
        if estudiante.curso_activo and estudiante.curso_activo in cursos_inscritos:
            curso_seleccionado = estudiante.curso_activo
        else:
            # 2. Si no ha elegido (o el elegido ya no es válido), usamos el primero por defecto
            curso_seleccionado = cursos_inscritos[0]
            # (Opcional) Guardamos este como default para la próxima
            estudiante.curso_activo = curso_seleccionado
            estudiante.save()

    # Obtener casos del curso seleccionado
    casos = []
    if curso_seleccionado:
        casos = Caso.objects.filter(curso=curso_seleccionado, estado='Activo')

    return render(request, 'usuarios/inicio.html', {
        'estudiante': estudiante,
        'cursos_inscritos': cursos_inscritos,
        'curso_activo': curso_seleccionado, # Enviamos el curso activo al template
        'casos': casos
    })





# applications/usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import Estudiante, Perfil
from applications.inscripciones.models import Solicitud_Inscripcion

# applications/usuarios/views.py

def ver_perfil(request):
    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)
    
    # Obtener cursos donde el estudiante fue aceptado
    solicitudes = Solicitud_Inscripcion.objects.filter(estudiante=estudiante, estado='aceptada')
    cursos_inscritos = [s.curso for s in solicitudes]

    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        # CASO A: Cambiar Contraseña
        if 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Mantiene la sesión activa
                messages.success(request, 'Tu contraseña ha sido actualizada.')
                return redirect('ver_perfil')
            else:
                messages.error(request, 'Error en la contraseña. Verifica los campos.')

        # CASO B: Guardar Ajustes (Puede venir de "Mis Cursos" o de "Ajustes")
        elif 'save_settings' in request.POST:
            
            # 1. ¿Viene de la pestaña "Ajustes" (Preferencias)?
            # Buscamos el campo oculto 'ajustes_generales' que pusimos en el HTML
            if 'ajustes_generales' in request.POST:
                estudiante.modo_oscuro = (request.POST.get('modo_oscuro') == 'on')
                estudiante.ocultar_instrucciones = (request.POST.get('ocultar_instrucciones') == 'on')
                messages.success(request, 'Preferencias de visualización actualizadas.')

            # 2. ¿Viene de la pestaña "Mis Cursos" (Selector de curso)?
            # Verificamos si el select 'curso_activo' está presente en los datos enviados
            if 'curso_activo' in request.POST:
                curso_id_seleccionado = request.POST.get('curso_activo')
                if curso_id_seleccionado:
                    # Validación de seguridad: el curso debe pertenecer a los inscritos
                    ids_validos = [c.id for c in cursos_inscritos]
                    if int(curso_id_seleccionado) in ids_validos:
                        estudiante.curso_activo_id = curso_id_seleccionado
                        messages.success(request, 'Curso principal actualizado.')
                    else:
                        messages.error(request, 'El curso seleccionado no es válido.')

            estudiante.save()
            return redirect('ver_perfil')

    return render(request, 'usuarios/perfil.html', {
        'estudiante': estudiante,
        'cursos_inscritos': cursos_inscritos,
        'password_form': password_form
    })