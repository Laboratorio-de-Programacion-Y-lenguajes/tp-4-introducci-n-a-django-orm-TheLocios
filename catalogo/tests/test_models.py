from __future__ import annotations

from datetime import date

from django.test import TestCase

from catalogo.models import Autor, Categoria, Libro, Prestamo


class ModelsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Datos compartidos para todos los tests de esta clase.
        setUpTestData corre una sola vez y envuelve todo en una transacción.
        """
        cls.autor = Autor.objects.create(
            nombre="Ursula K. Le Guin",
            email="ursula@example.com",
            biografia="Autora de ciencia ficción y fantasía.",
        )

        cls.cat_sf = Categoria.objects.create(nombre="ciencia ficción")
        cls.cat_fant = Categoria.objects.create(nombre="fantasía")

        cls.libro = Libro.objects.create(
            titulo="Los desposeídos",
            isbn="978-0000000001",
            fecha_publicacion=date(1974, 1, 1),
            cantidad_total=2,
            autor=cls.autor,
        )
        cls.libro.categorias.add(cls.cat_sf, cls.cat_fant)

    def test_modelos_se_crean(self):
        """Verifica que los modelos se crean correctamente en la BD."""
        self.assertEqual(Autor.objects.count(), 1)
        self.assertEqual(Categoria.objects.count(), 2)
        self.assertEqual(Libro.objects.count(), 1)

    def test_relacion_fk_libro_autor(self):
        """El libro debe tener referencia a su autor."""
        libro = Libro.objects.select_related("autor").get(pk=self.libro.pk)
        self.assertEqual(libro.autor.nombre, "Ursula K. Le Guin")

    def test_relacion_m2m_libro_categoria(self):
        """El libro debe estar asociado a las dos categorías."""
        categorias = list(self.libro.categorias.values_list("nombre", flat=True))
        self.assertIn("ciencia ficción", categorias)
        self.assertIn("fantasía", categorias)

    def test_disponibilidad_sin_prestamos(self):
        """Sin préstamos activos, todos los ejemplares están disponibles."""
        self.assertEqual(self.libro.prestamos_activos(), 0)
        self.assertEqual(self.libro.disponibles(), 2)
        self.assertTrue(self.libro.tiene_disponibles())

    def test_disponibilidad_con_prestamos_activos(self):
        """Dos préstamos activos sobre 2 ejemplares => disponibles = 0."""
        Prestamo.objects.create(
            libro=self.libro,
            nombre_prestatario="Ana",
            fecha_prestamo=date(2026, 3, 1),
            fecha_devolucion=None,  # activo
        )
        Prestamo.objects.create(
            libro=self.libro,
            nombre_prestatario="Juan",
            fecha_prestamo=date(2026, 3, 2),
            fecha_devolucion=None,  # activo
        )

        self.libro.refresh_from_db()
        self.assertEqual(self.libro.prestamos_activos(), 2)
        self.assertEqual(self.libro.disponibles(), 0)
        self.assertFalse(self.libro.tiene_disponibles())

    def test_prestamo_devuelto_no_cuenta_como_activo(self):
        """Un préstamo con fecha_devolucion != NULL no debe contarse como activo."""
        Prestamo.objects.create(
            libro=self.libro,
            nombre_prestatario="Luz",
            fecha_prestamo=date(2026, 3, 1),
            fecha_devolucion=date(2026, 3, 10),  # devuelto
        )
        self.libro.refresh_from_db()
        self.assertEqual(self.libro.prestamos_activos(), 0)
        self.assertEqual(self.libro.disponibles(), 2)
        self.assertTrue(self.libro.tiene_disponibles())
