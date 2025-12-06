from django.contrib import admin
from .models import Curso, Aprendizaje_Esperado

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    # Columnas: Nombre, Docente, Estado, Fechas y Objetivo
    list_display = ('nombre', 'docente_nombre', 'estado', 'fecha_inicio', 'fecha_fin', 'objetivo')
    
    # Filtros: Estado (Activo/Inactivo), Fecha de inicio y Docente
    list_filter = ('estado', 'fecha_inicio', 'docente')
    
    # Buscador: Por nombre del curso o nombre del docente
    search_fields = ('nombre', 'docente__perfil__user__first_name', 'docente__perfil__user__last_name')

    # Función para mostrar nombre del docente en la tabla
    def docente_nombre(self, obj):
        if obj.docente:
            return f"{obj.docente.perfil.user.first_name} {obj.docente.perfil.user.last_name}"
        return "Sin Docente"
    docente_nombre.short_description = 'Docente'

@admin.register(Aprendizaje_Esperado)
class AprendizajeEsperadoAdmin(admin.ModelAdmin):
    # Columnas
    list_display = ('nombre', 'nivel_bonito')
    
    # Filtro por nivel (Básico, Intermedio, Avanzado)
    list_filter = ('nivel',)
    
    # Buscador por nombre o descripción
    search_fields = ('nombre', 'descripcion')

    # Muestra el nivel con la primera letra mayúscula (estético)
    def nivel_bonito(self, obj):
        return obj.get_nivel_display()
    nivel_bonito.short_description = 'Nivel'