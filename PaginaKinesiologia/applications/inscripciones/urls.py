from django.urls import path
from .views import inscribirse

urlpatterns = [
    path('inscribirse/', inscribirse, name='inscribirse'),
]
