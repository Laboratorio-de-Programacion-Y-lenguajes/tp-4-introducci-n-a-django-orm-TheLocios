from __future__ import annotations

from django.db import models
from django.utils import timezone


class Autor(models.Model):
    """
    Representa a un autor
    nombre, email unico, biografia opcional
    """
    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    biografia = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.nombre


class Categoria(models.Model):
    """
    Categoria temática de libros
    'fantasía', 'ciencia ficción', 'historia'
    """
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.nombre


class Libro(models.Model):
    """
    Libro del catálogo de la biblioteca
    N:1 con Autor y N:M con Categoria
    """
    titulo = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True)
    fecha_publicacion = models.DateField()
    cantidad_total = models.PositiveIntegerField()
    autor = models.ForeignKey(Autor, on_delete=models.PROTECT)
    categorias = models.ManyToManyField(Categoria)

    def __str__(self) -> str:
        return self.titulo

    def prestamos_activos(self) -> int:
        """
        Retorna la cantidad de prestamos activos (fecha_devolucion IS NULL)
        """
        return self.prestamo_set.filter(fecha_devolucion__isnull=True).count()

    def disponibles(self) -> int:
        """
        Retorna cuantas copias estan disponibles:
        cantidad_total - prestamos_activos()
        """
        return self.cantidad_total - self.prestamos_activos()

    def tiene_disponibles(self) -> bool:
        """Retorna True si hay al menos una copia disponible."""
        return self.disponibles() > 0


class Prestamo(models.Model):
    """
    Registro de un prestamo de libro a un usuario
    if fecha_devolucion NULL → prestamo activo
    """
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    nombre_prestatario = models.CharField(max_length=150)
    fecha_prestamo = models.DateField(default=timezone.now)
    fecha_devolucion = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.libro.titulo} prestado a {self.nombre_prestatario}"