from django.db import models

# Create your models here.

class Docente(models.Model):
    nombre = models.CharField('Nombre', max_length=150)
    apellido = models.CharField('Apellido', max_length=150)
    correo = models.EmailField('Correo electrónico', max_length=150, unique=True)
    contrasena = models.CharField('Contraseña', max_length=150)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) + '-' + self.nombre

class Aprendizaje_Esperado(models.Model):
    nombre = models.CharField('Nombre del Objetivo', max_length=150)
    descripcion = models.TextField('Descripción')
    nivel = models.CharField('Nivel', max_length=50, choices=[('básico', 'Básico'), ('intermedio', 'Intermedio'), ('avanzado', 'Avanzado')])

    def __str__(self):
        return str(self.id) + '-' + self.nombre

class Curso(models.Model):
    nombre = models.CharField('Nombre del Curso', max_length=150)
    descripcion = models.TextField('Descripción')
    programa = models.TextField('Programa')
    estado = models.CharField('Estado', max_length=10, choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')])
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    objetivo = models.ForeignKey(Aprendizaje_Esperado, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + '-' + self.nombre

class Categoria_Clinica(models.Model):
    nombre = models.CharField('Categoría Clínica', max_length=150)
    descripcion = models.TextField('Descripción')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + '-' + self.nombre