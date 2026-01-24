from django.contrib import admin

# Register your models here.

from .models import Variedad

@admin.register(Variedad)
class VariedadAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "fecha_creacion")
    search_fields = ("nombre",)
    ordering = ("nombre",)
