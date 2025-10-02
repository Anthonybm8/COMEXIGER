from django.db import models

class Usuario(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    mesa = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)