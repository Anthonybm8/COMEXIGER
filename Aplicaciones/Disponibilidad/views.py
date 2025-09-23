from django.shortcuts import render,redirect
from django.contrib import messages
def inicio(request):
    return render(request,"disponibilidad.html")