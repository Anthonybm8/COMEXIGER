from django.urls import path
from . import views

urlpatterns = [
    path('rendimiento/', views.inicio, name='rendimiento'),

]
