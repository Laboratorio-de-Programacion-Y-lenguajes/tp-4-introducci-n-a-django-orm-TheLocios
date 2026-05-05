from __future__ import annotations

from django.db.models import Count, Q, F
from .models import Autor, Libro


def libros_por_categoria(nombre_categoria: str):
    """
    Devuelve Libros que pertenecen a la categoria
    """
    return Libro.objects.filter(categorias__nombre=nombre_categoria)


def autores_con_mas_de_n_libros(n: int):
    """
    Devuelve Autores que tienen más de n libros en el catalogo
    """
    return Autor.objects.annotate(cantidad_libros=Count("libro")).filter(cantidad_libros__gt=n)


def libros_sin_disponibilidad():
    """
    Devuelve Libros donde no hay copias disponibles
    (prestamos_activos == cantidad_total)
    """
    return Libro.objects.annotate(
        activos=Count("prestamo", filter=Q(prestamo__fecha_devolucion__isnull=True))
    ).filter(activos=F("cantidad_total"))


def top_n_libros_mas_prestados(n: int):
    """
    Devuelve los N libros con más prestamos (en total, sin importar si están activos)
    """
    return Libro.objects.annotate(
        total_prestamos=Count("prestamo")
    ).order_by("-total_prestamos")[:n]
    