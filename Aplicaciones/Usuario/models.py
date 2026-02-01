from django.db import models
from django.contrib.auth.hashers import make_password, check_password
class Mesa(models.Model):
    nombre = models.CharField(max_length=100, unique=True) 

    def __str__(self):
        return self.nombre
    
class Usuario(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    mesa = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)


    
    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.username})"
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    @property
    def is_authenticated(self):
        return True