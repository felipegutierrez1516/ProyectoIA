# Dockerfile
FROM python:3.11-slim

# Evitar que Python cree archivos .pyc y forzar salida directa en logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto
COPY . .

# Crear carpetas para archivos estáticos y media
RUN mkdir -p /vol/staticfiles /vol/media

# ⚠️ No ejecutamos collectstatic aquí, porque Django aún no tiene acceso a settings ni .env
# RUN python manage.py collectstatic --noinput

# Exponer el puerto 8000
EXPOSE 8000

# Comando por defecto: iniciar Gunicorn
CMD ["gunicorn", "PaginaKinesiologia.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

