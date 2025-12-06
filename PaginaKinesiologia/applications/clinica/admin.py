from django.contrib import admin
from django import forms
from .models import Caso, Paciente_Ficticio, Etapa, Tema_Interrogacion, Partes_del_Cuerpo, COORDS_MAP

# --- DEFINICIÓN DE INLINES (Formularios anidados) ---

# Permite agregar Pacientes directamente desde la pantalla del Caso
class PacienteInline(admin.TabularInline):
    model = Paciente_Ficticio
    extra = 1  # Muestra una fila vacía para agregar rápido
    fields = ('nombre', 'edad', 'genero', 'descripcion')
    show_change_link = True # Permite ir al detalle del paciente si se necesita editar más a fondo

# Permite agregar Etapas directamente desde la pantalla del Paciente
class EtapaInline(admin.TabularInline):
    model = Etapa
    extra = 0
    fields = ('nombre', 'video', 'descripcion')
    show_change_link = True


# --- CONFIGURACIÓN DE LOS MODELOS ---

# 1. Admin para CASO
@admin.register(Caso)
class CasoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'curso', 'estado', 'pacientes_count')
    list_filter = ('estado', 'curso')
    search_fields = ('titulo', 'descripcion')
    
    # Agregamos el Inline para gestionar pacientes aquí mismo
    inlines = [PacienteInline]

    def pacientes_count(self, obj):
        return obj.pacientes.count()
    pacientes_count.short_description = 'Nº Pacientes'


# 2. Admin para PACIENTE
@admin.register(Paciente_Ficticio)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'edad', 'genero', 'caso')
    list_filter = ('genero', 'caso')
    search_fields = ('nombre',)
    
    # Agregamos el Inline para ver/crear etapas desde el paciente
    inlines = [EtapaInline]


# 3. Admin para ETAPA
@admin.register(Etapa)
class EtapaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'paciente', 'video_link')
    list_filter = ('nombre', 'paciente__caso') # Filtra por tipo de etapa y por caso del paciente
    search_fields = ('paciente__nombre',)

    def video_link(self, obj):
        return obj.video
    video_link.short_description = 'Video URL'


# 4. Admin para TEMA INTERROGACION
@admin.register(Tema_Interrogacion)
class TemaInterrogacionAdmin(admin.ModelAdmin):
    # Columnas que se verán en la tabla
    list_display = ('pregunta_corta', 'es_correcta', 'etapa_info')
    # Filtros laterales
    list_filter = ('es_correcta', 'etapa__nombre', 'etapa__paciente__caso')
    # Barra de búsqueda
    search_fields = ('pregunta', 'respuesta')

    def pregunta_corta(self, obj):
        return obj.pregunta[:80] + "..." if len(obj.pregunta) > 80 else obj.pregunta
    pregunta_corta.short_description = 'Pregunta'

    def etapa_info(self, obj):
        return f"{obj.etapa.nombre} ({obj.etapa.paciente.nombre})"
    etapa_info.short_description = 'Etapa / Paciente'


# 5. Admin para PARTES DEL CUERPO
class PartesForm(forms.ModelForm):
    class Meta:
        model = Partes_del_Cuerpo
        fields = ['etapa', 'nombre', 'descripcion', 'left', 'top', 'correcta']

    def clean(self):
        cleaned = super().clean()
        nombre = (cleaned.get('nombre') or '').strip().lower()
        left = cleaned.get('left') or 0
        top = cleaned.get('top') or 0
        
        # Lógica de autocompletado de coordenadas
        if (left == 0 or left is None) and (top == 0 or top is None) and nombre in COORDS_MAP:
            cleaned['left'], cleaned['top'] = COORDS_MAP[nombre]
        return cleaned

@admin.register(Partes_del_Cuerpo)
class PartesDelCuerpoAdmin(admin.ModelAdmin):
    form = PartesForm
    list_display = ('nombre', 'etapa', 'correcta', 'coords_info') 
    list_filter = ('correcta', 'etapa__nombre', 'nombre') 
    search_fields = ('descripcion',)
    
    def coords_info(self, obj):
        return f"L:{obj.left}% T:{obj.top}%"
    coords_info.short_description = 'Coordenadas'

    class Media:
        js = ('js/ubicacion_automatica.js',)