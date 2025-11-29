from django.db import models
from applications.cursos.models import Curso
from applications.usuarios.models import Docente

# Create your models here.

class Caso(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='casos')
    titulo = models.CharField(max_length=50)  # Cervical, Lumbar, etc.
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')])

    def __str__(self):
        return self.titulo
    

class Paciente_Ficticio(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    edad = models.IntegerField()
    genero = models.CharField(max_length=50)
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE, related_name='pacientes', null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.nombre}"


class Etapa(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    video = models.URLField()
    paciente = models.ForeignKey(Paciente_Ficticio, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.nombre}"


class Tema_Interrogacion(models.Model):
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    pregunta = models.TextField()
    respuesta = models.TextField()
    es_correcta = models.BooleanField(default=False)
    justificacion_error = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}"



# applications/clinica/models.py

PARTES_CHOICES = [
    ('cabeza', 'Cabeza'),
    ('cuello', 'Cuello'),
    ('hombro_izquierdo', 'Hombro Izquierdo'),
    ('hombro_derecho', 'Hombro Derecho'),
    ('codo_izquierdo', 'Codo Izquierdo'),
    ('codo_derecho', 'Codo Derecho'),
    ('mano_izquierda', 'Mano Izquierda'),
    ('mano_derecha', 'Mano Derecha'),
    ('pecho', 'Pecho'),
    ('espalda', 'Espalda'),
    ('abdomen', 'Abdomen'),
    ('pelvis', 'Pelvis'),
    ('muslo_izquierdo', 'Muslo Izquierdo'),
    ('muslo_derecho', 'Muslo Derecho'),
    ('rodilla_izquierda', 'Rodilla Izquierda'),
    ('rodilla_derecha', 'Rodilla Derecha'),
    ('pie_izquierdo', 'Pie Izquierdo'),
    ('pie_derecho', 'Pie Derecho'),
]

# Mapa de Coordenadas en Porcentajes (Left %, Top %)
# Estos valores ubican los puntos correctamente sin importar el tamaño de la imagen.
COORDS_MAP = {
    'cabeza': (50, 6),
    'cuello': (50, 13),
    'hombro_izquierdo': (32, 18),
    'hombro_derecho': (68, 18),
    'pecho': (50, 23),
    'espalda': (50, 23),  # Ubicación aproximada en tórax
    'codo_izquierdo': (27, 29),
    'codo_derecho': (73, 29),
    'abdomen': (50, 34),
    'mano_izquierda': (21, 42),
    'mano_derecha': (79, 42),
    'pelvis': (50, 44),
    'muslo_izquierdo': (42, 53),
    'muslo_derecho': (58, 53),
    'rodilla_izquierda': (42, 69),
    'rodilla_derecha': (58, 69),
    'pie_izquierdo': (42, 90),
    'pie_derecho': (58, 90),
}

class Partes_del_Cuerpo(models.Model):
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=150, choices=PARTES_CHOICES)
    descripcion = models.TextField()
    left = models.IntegerField(default=0, help_text="Posición Horizontal en % (0-100)")
    top = models.IntegerField(default=0, help_text="Posición Vertical en % (0-100)")
    correcta = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} - {self.nombre}"