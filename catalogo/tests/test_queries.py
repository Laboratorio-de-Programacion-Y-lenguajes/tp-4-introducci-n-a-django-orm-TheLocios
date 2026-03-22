from __future__ import annotations

from datetime import date

from django.test import TestCase

from catalogo.models import Autor, Categoria, Libro, Prestamo
from catalogo import queries


class QueriesTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Dataset compartido para los tests de consultas.

        Estructura de datos:
        - a1: Tolkien → l1 (El Hobbit, cat=fantasía), l2 (El Señor de los Anillos, cat=fantasía)
        - a2: Asimov  → l3 (Fundación, cat=ciencia ficción)

        Préstamos:
        - l1: 1 activo  → sin disponibilidad (cantidad_total=1)
        - l2: 1 devuelto + 1 activo → disponible 1 (cantidad_total=2)
        - l3: 3 devueltos → disponible 1, es el más prestado (cantidad_total=1)
        """
        cls.a1 = Autor.objects.create(
            nombre="J. R. R. Tolkien",
            email="tolkien@example.com",
            biografia="Autor de fantasía.",
        )
        cls.a2 = Autor.objects.create(
            nombre="Isaac Asimov",
            email="asimov@example.com",
            biografia="Autor de ciencia ficción.",
        )

        cls.c1 = Categoria.objects.create(nombre="fantasía")
        cls.c2 = Categoria.objects.create(nombre="ciencia ficción")

        cls.l1 = Libro.objects.create(
            titulo="El Hobbit",
            isbn="978-0000000002",
            fecha_publicacion=date(1937, 1, 1),
            cantidad_total=1,
            autor=cls.a1,
        )
        cls.l1.categorias.add(cls.c1)

        cls.l2 = Libro.objects.create(
            titulo="El Señor de los Anillos",
            isbn="978-0000000003",
            fecha_publicacion=date(1954, 1, 1),
            cantidad_total=2,
            autor=cls.a1,
        )
        cls.l2.categorias.add(cls.c1)

        cls.l3 = Libro.objects.create(
            titulo="Fundación",
            isbn="978-0000000004",
            fecha_publicacion=date(1951, 1, 1),
            cantidad_total=1,
            autor=cls.a2,
        )
        cls.l3.categorias.add(cls.c2)

        # l1: 1 préstamo activo
        Prestamo.objects.create(
            libro=cls.l1,
            nombre_prestatario="Ana",
            fecha_prestamo=date(2026, 3, 1),
            fecha_devolucion=None,
        )

        # l2: 1 devuelto + 1 activo
        Prestamo.objects.create(
            libro=cls.l2,
            nombre_prestatario="Juan",
            fecha_prestamo=date(2026, 3, 1),
            fecha_devolucion=date(2026, 3, 10),
        )
        Prestamo.objects.create(
            libro=cls.l2,
            nombre_prestatario="Luz",
            fecha_prestamo=date(2026, 3, 12),
            fecha_devolucion=None,
        )

        # l3: 3 devueltos (el más prestado históricamente)
        Prestamo.objects.create(
            libro=cls.l3,
            nombre_prestatario="P1",
            fecha_prestamo=date(2026, 3, 1),
            fecha_devolucion=date(2026, 3, 2),
        )
        Prestamo.objects.create(
            libro=cls.l3,
            nombre_prestatario="P2",
            fecha_prestamo=date(2026, 3, 3),
            fecha_devolucion=date(2026, 3, 4),
        )
        Prestamo.objects.create(
            libro=cls.l3,
            nombre_prestatario="P3",
            fecha_prestamo=date(2026, 3, 5),
            fecha_devolucion=date(2026, 3, 6),
        )

    def test_libros_por_categoria_devuelve_correctos(self):
        """Libros de categoría 'fantasía' = El Hobbit y El Señor de los Anillos."""
        qs = queries.libros_por_categoria("fantasía")
        titulos = list(qs.values_list("titulo", flat=True))
        self.assertIn("El Hobbit", titulos)
        self.assertIn("El Señor de los Anillos", titulos)
        self.assertNotIn("Fundación", titulos)

    def test_libros_por_categoria_sin_resultados(self):
        """Una categoría inexistente no devuelve resultados."""
        qs = queries.libros_por_categoria("categoría inexistente")
        self.assertEqual(qs.count(), 0)

    def test_autores_con_mas_de_n_libros(self):
        """Tolkien tiene 2 libros, Asimov tiene 1. Con n=1 solo aparece Tolkien."""
        qs = queries.autores_con_mas_de_n_libros(1)
        nombres = list(qs.values_list("nombre", flat=True))
        self.assertIn("J. R. R. Tolkien", nombres)
        self.assertNotIn("Isaac Asimov", nombres)

    def test_autores_con_mas_de_n_libros_todos(self):
        """Con n=0 deben aparecer ambos autores."""
        qs = queries.autores_con_mas_de_n_libros(0)
        self.assertEqual(qs.count(), 2)

    def test_libros_sin_disponibilidad(self):
        """El Hobbit (1 total, 1 activo) no tiene disponibilidad."""
        qs = queries.libros_sin_disponibilidad()
        titulos = list(qs.values_list("titulo", flat=True))
        self.assertIn("El Hobbit", titulos)
        self.assertNotIn("El Señor de los Anillos", titulos)
        self.assertNotIn("Fundación", titulos)

    def test_top_n_libros_mas_prestados(self):
        """Fundación tiene 3 préstamos, debe aparecer primero. El top 2 incluye 2 libros."""
        qs = queries.top_n_libros_mas_prestados(2)
        titulos = list(qs.values_list("titulo", flat=True))
        self.assertEqual(titulos[0], "Fundación")
        self.assertEqual(len(titulos), 2)

    def test_top_1_libro_mas_prestado(self):
        """top_n_libros_mas_prestados(1) solo devuelve 1 resultado."""
        qs = queries.top_n_libros_mas_prestados(1)
        self.assertEqual(len(list(qs)), 1)
