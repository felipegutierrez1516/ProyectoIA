from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from applications.usuarios.models import Estudiante
from applications.inscripciones.models import Solicitud_Inscripcion
from applications.clinica.models import Caso
# Importamos ambos modelos para calcular puntajes
from applications.evaluaciones.models import Evaluacion, Respuesta_Evaluacion 

def login_view(request):
    # ... (Tu código de login se mantiene igual) ...
    from django.contrib.auth import authenticate, login
    from applications.usuarios.models import Perfil
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

def registro_view(request):
    # ... (Tu código de registro se mantiene igual) ...
    from django.contrib.auth.models import User
    from django.contrib.auth.hashers import make_password
    from applications.usuarios.models import Perfil, Estudiante, Docente
    
    if request.method == 'POST':
        password = request.POST['password']
        email = request.POST['email'].lower()
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = email 
        
        if User.objects.filter(username=username).exists():
            return render(request, 'usuarios/registro.html', {'error': 'Este correo ya está registrado.'})

        user = User.objects.create(
            username=username,
            password=make_password(password),
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        if email.endswith('@alumnos.ucn.cl'):
            rol = 'estudiante'
        elif email.endswith('@ucn.cl'):
            rol = 'docente'
        else:
            rol = 'estudiante'

        perfil, creado = Perfil.objects.get_or_create(user=user, defaults={'rol': rol})

        if rol == 'estudiante':
            Estudiante.objects.get_or_create(perfil=perfil)
        else:
            Docente.objects.get_or_create(perfil=perfil)

        return redirect('login')

    return render(request, 'usuarios/registro.html')

def ver_perfil(request):
    # ... (Tu código de perfil se mantiene igual) ...
    from django.contrib import messages
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.forms import PasswordChangeForm
    from .models import Estudiante, Perfil
    
    perfil = Perfil.objects.get(user=request.user)
    estudiante = Estudiante.objects.get(perfil=perfil)
    
    solicitudes = Solicitud_Inscripcion.objects.filter(estudiante=estudiante, estado='aceptada')
    cursos_inscritos = [s.curso for s in solicitudes]

    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        if 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Tu contraseña ha sido actualizada.')
                return redirect('ver_perfil')
            else:
                messages.error(request, 'Error en la contraseña.')

        elif 'save_settings' in request.POST:
            if 'ajustes_generales' in request.POST:
                estudiante.modo_oscuro = (request.POST.get('modo_oscuro') == 'on')
                estudiante.ocultar_instrucciones = (request.POST.get('ocultar_instrucciones') == 'on')
                messages.success(request, 'Preferencias actualizadas.')

            if 'curso_activo' in request.POST:
                curso_id_seleccionado = request.POST.get('curso_activo')
                if curso_id_seleccionado:
                    ids_validos = [c.id for c in cursos_inscritos]
                    if int(curso_id_seleccionado) in ids_validos:
                        estudiante.curso_activo_id = curso_id_seleccionado
                        messages.success(request, 'Curso actualizado.')
                    else:
                        messages.error(request, 'Curso no válido.')

            estudiante.save()
            return redirect('ver_perfil')

    return render(request, 'usuarios/perfil.html', {
        'estudiante': estudiante,
        'cursos_inscritos': cursos_inscritos,
        'password_form': password_form
    })

# --- VISTA MODIFICADA CON ENVÍO AL DOCENTE ---
# applications/usuarios/views.py

# ... imports ...
from django.utils import timezone # Asegúrate de importar timezone

def inicio_estudiante(request):
    estudiante = Estudiante.objects.get(perfil__user=request.user)
    
    # --- CAMBIO IMPORTANTE AQUÍ ---
    if request.method == 'POST' and request.POST.get('enviar_correo') == 'true':
        
        # 1. Buscamos la evaluación que está PENDIENTE (en_curso) para cerrarla
        evaluacion_a_cerrar = Evaluacion.objects.filter(
            estudiante=estudiante, 
            estado='en_curso'
        ).last()

        if evaluacion_a_cerrar:
            # 2. CAMBIAMOS ESTADO A 'FINALIZADA' AHORA (Al hacer clic en el botón)
            evaluacion_a_cerrar.estado = 'finalizada'
            evaluacion_a_cerrar.fecha_evaluacion = timezone.now()
            evaluacion_a_cerrar.save()
            
            # Limpiamos la variable de sesión del cronómetro
            if 'inicio_evaluacion' in request.session:
                del request.session['inicio_evaluacion']

            # 3. Lógica de envío de correo (usando los datos de esta evaluación)
            curso = evaluacion_a_cerrar.paciente.caso.curso
            docente = curso.docente
            docente_email = docente.perfil.user.email
            docente_nombre = f"{docente.perfil.user.first_name} {docente.perfil.user.last_name}"

            respuestas = Respuesta_Evaluacion.objects.filter(evaluacion=evaluacion_a_cerrar)
            total_intentos = respuestas.count()
            correctas = respuestas.filter(correcta=True).count()
            fecha_str = evaluacion_a_cerrar.fecha_evaluacion.strftime("%d/%m/%Y %H:%M")

            asunto = f"[Evaluación Clínica] {estudiante.perfil.user.first_name} {estudiante.perfil.user.last_name} - {evaluacion_a_cerrar.paciente.nombre}"
            
            mensaje = f"""
            Estimado/a Docente {docente_nombre},

            El estudiante {estudiante.perfil.user.first_name} {estudiante.perfil.user.last_name} ha finalizado exitosamente una evaluación.

            RESUMEN:
            Curso: {curso.nombre}
            Paciente: {evaluacion_a_cerrar.paciente.nombre}
            Fecha: {fecha_str}
            
            DESEMPEÑO:
            >> {correctas} respuestas correctas de {total_intentos} intentos totales.

            DIAGNÓSTICO:
            {evaluacion_a_cerrar.diagnostico}

            Atte,
            Plataforma Kinesiología UCN
            """
            
            send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [docente_email], fail_silently=False)
            print(f"\n--- EVALUACIÓN CERRADA Y CORREO ENVIADO A {docente_email} ---\n")
            
        return redirect('inicio_estudiante')

    # ... resto de la vista normal (carga de cursos, etc.) ...
    solicitudes = Solicitud_Inscripcion.objects.filter(estudiante=estudiante, estado='aceptada')
    # ... (el código sigue igual)
    cursos_inscritos = [s.curso for s in solicitudes]

    curso_seleccionado = None
    if cursos_inscritos:
        if estudiante.curso_activo and estudiante.curso_activo in cursos_inscritos:
            curso_seleccionado = estudiante.curso_activo
        else:
            curso_seleccionado = cursos_inscritos[0]
            estudiante.curso_activo = curso_seleccionado
            estudiante.save()

    casos = []
    if curso_seleccionado:
        casos = Caso.objects.filter(curso=curso_seleccionado, estado='Activo')

    return render(request, 'usuarios/inicio.html', {
        'estudiante': estudiante,
        'cursos_inscritos': cursos_inscritos,
        'curso_activo': curso_seleccionado,
        'casos': casos
    })


def redireccion_inicio(request):
    return redirect('login')  # o 'inicio_estudiante' si ya está logueado