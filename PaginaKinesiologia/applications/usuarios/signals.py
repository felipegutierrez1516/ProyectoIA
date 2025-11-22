from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from applications.usuarios.models import Perfil

@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        correo = instance.email.lower()
        if correo.endswith('@alumnos.ucn.cl'):
            rol = 'estudiante'
        elif correo.endswith('@ucn.cl'):
            rol = 'docente'
        else:
            rol = 'estudiante'  # por defecto
        Perfil.objects.create(user=instance, rol=rol)
