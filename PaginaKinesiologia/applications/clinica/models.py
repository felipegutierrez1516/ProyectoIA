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
    docente_asignado = models.ForeignKey(Docente, on_delete=models.SET_NULL, null=True)

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



PARTES_CHOICES = [
    ('cabeza', 'Cabeza'),
    ('cuello', 'Cuello'),
    ('mano_izquierda', 'Mano Izquierda'),
    ('mano_derecha', 'Mano Derecha'),
    ('codo_izquierdo', 'Codo Izquierdo'),
    ('codo_derecho', 'Codo Derecho'),
    ('hombro_izquierdo', 'Hombro Izquierdo'),
    ('hombro_derecho', 'Hombro Derecho'),
    ('espalda', 'Espalda'),
    ('pecho', 'Pecho'),
    ('abdomen', 'Abdomen'),
    ('pelvis', 'Pelvis'),
    ('muslo_izquierdo', 'Muslo Izquierdo'),
    ('muslo_derecho', 'Muslo Derecho'),
    ('rodilla_izquierda', 'Rodilla Izquierda'),
    ('rodilla_derecha', 'Rodilla Derecha'),
    ('pie_izquierdo', 'Pie Izquierdo'),
    ('pie_derecho', 'Pie Derecho'),
]

COORDS_MAP = {
    'cabeza': (270, 40),
    'cuello': (270, 90),
    'hombro_izquierdo': (220, 120),
    'hombro_derecho': (320, 120),
    'codo_izquierdo': (200, 180),
    'codo_derecho': (340, 180),
    'mano_izquierda': (180, 240),
    'mano_derecha': (360, 240),
    'espalda': (270, 160),
    'pecho': (270, 140),
    'abdomen': (270, 200),
    'pelvis': (270, 250),
    'muslo_izquierdo': (240, 300),
    'muslo_derecho': (300, 300),
    'rodilla_izquierda': (240, 370),
    'rodilla_derecha': (300, 370),
    'pie_izquierdo': (240, 460),
    'pie_derecho': (300, 460),
}

class Partes_del_Cuerpo(models.Model):
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=150, choices=PARTES_CHOICES)
    descripcion = models.TextField()
    left = models.IntegerField(default=0)
    top = models.IntegerField(default=0)
    correcta = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} - {self.nombre}"