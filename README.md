# TP 4 · Introducción a Django ORM y Persistencia

**Stack**: Python 3.13+, Django 5.1+, SQLite, Django ORM, Django `unittest`, Git/GitHub Classroom  
**Entrega**: Repositorio de GitHub Classroom con autograding (GitHub Actions) — push a `main`.

---

## 1) Objetivo

Modelar una **biblioteca universitaria** con Django ORM: autores, libros, categorías y préstamos. Desarrollar consultas complejas con el ORM y validarlas con tests unitarios usando `django.test.TestCase`.

Relevancia profesional: En la industria, la persistencia de datos es central en casi toda aplicación. Django ORM resuelve el mapeo objeto-relacional de forma segura y mantenible, sin escribir SQL crudo. Es la base de cualquier proyecto Django real.

Qué van a construir:

- Un módulo `catalogo/models.py` con 4 modelos y relaciones (FK y M2M).
- Un módulo `catalogo/queries.py` con 4 funciones de consulta ORM.
- Tests con `django.test.TestCase` que validan modelos, reglas de negocio y consultas.
- Autograding con GitHub Actions.

---

## 2) Instalación de Python y pip (guía rápida)

### Windows (10/11)

1. Descargá Python 3.13.x desde [python.org/downloads](https://www.python.org/downloads/).
2. Durante la instalación, marcá **"Add Python to PATH"** → Install Now.
3. Verificá en PowerShell o CMD:
   ```
   python --version
   pip --version
   ```
Si `python` no se reconoce, reiniciá la terminal o reinstalá marcando "Add Python to PATH".

### macOS

1. Instalá con [Homebrew](https://brew.sh/):
   ```
   brew install python@3.13
   ```
2. Verificá:
   ```
   python3 --version
   pip3 --version
   ```

> En macOS los comandos suelen ser `python3` y `pip3`.

### Linux (Ubuntu/Debian)

```
sudo apt update
sudo apt install python3 python3-pip
python3 --version
pip3 --version
```

---

## 3) Setup del proyecto

### 1. Cloná tu repo de Classroom

```
git clone <URL-del-repo-asignado>
cd <carpeta-del-repo>
```

### 2. Creá un entorno virtual (recomendado)

Windows (PowerShell):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalá dependencias

```
pip install -r requirements.txt
```

### 4. Generá y aplicá las migraciones

(después de completar `catalogo/models.py`)

```
python manage.py makemigrations
python manage.py migrate
```

---

## 4) Ejecutar los tests

```
# Todos los tests con detalle
python manage.py test -v 2
```

```
# Solo tests de modelos
python manage.py test catalogo.tests.test_models -v 2
```

```
# Solo tests de consultas
python manage.py test catalogo.tests.test_queries -v 2
```

---

## 5) Estructura del repositorio

```
.
├── biblioteca/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── catalogo/
│   ├── __init__.py
│   ├── apps.py
│   ├── admin.py
│   ├── models.py               ← Implementar aquí
│   ├── queries.py              ← Implementar aquí
│   ├── migrations/
│   │   └── __init__.py         ← Generar con makemigrations
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py      ← Tests de modelos y reglas de negocio
│       └── test_queries.py     ← Tests de las 4 consultas ORM
├── .github/
│   └── workflows/
│       └── autograding.yml
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 6) Archivos a completar

Hay dos archivos principales para implementar. Cada uno ya tiene comentarios guía con pistas sobre cómo usar el ORM.

| Archivo | Qué implementar | Excepción esperada |
|---------|----------------|--------------------|
| `catalogo/models.py` → `Autor` | `nombre`, `email` (único), `biografia` (opcional) | — |
| `catalogo/models.py` → `Categoria` | `nombre` (único) | — |
| `catalogo/models.py` → `Libro` | FK a `Autor`, M2M a `Categoria`, campos de catálogo | — |
| `catalogo/models.py` → `Prestamo` | FK a `Libro`, fechas, `fecha_devolucion` nullable | — |
| `catalogo/models.py` → `Libro.prestamos_activos()` | Cuenta préstamos con `fecha_devolucion IS NULL` | `NotImplementedError` hasta completar |
| `catalogo/models.py` → `Libro.disponibles()` | `cantidad_total - prestamos_activos()` | `NotImplementedError` hasta completar |
| `catalogo/models.py` → `Libro.tiene_disponibles()` | `True` si `disponibles() > 0` | `NotImplementedError` hasta completar |
| `catalogo/queries.py` → `libros_por_categoria` | Libros filtrados por nombre de categoría | `NotImplementedError` hasta completar |
| `catalogo/queries.py` → `autores_con_mas_de_n_libros` | Autores con más de N libros (annotate + filter) | `NotImplementedError` hasta completar |
| `catalogo/queries.py` → `libros_sin_disponibilidad` | Libros con disponibles == 0 (ORM puro) | `NotImplementedError` hasta completar |
| `catalogo/queries.py` → `top_n_libros_mas_prestados` | Top N por cantidad de préstamos total | `NotImplementedError` hasta completar |

Tu tarea: completar `models.py` y `queries.py` siguiendo los comentarios `# TODO` de cada archivo.

---

## 7) Cómo se entrega

1. Completá los modelos en `catalogo/models.py`.
2. Corré `python manage.py makemigrations && python manage.py migrate`.
3. Completá las consultas en `catalogo/queries.py`.
4. Verificá con `python manage.py test -v 2`.
5. Hacé ≥ 8 commits significativos (ej: `"feat: modelos Autor y Categoria"`, `"feat: queries libros_por_categoria"`).
6. Hacé `push` a `main`.
7. Revisá GitHub → **Actions** para ver si quedó ✅.

---

## 8) Modelos y consultas (`catalogo/`)

| Modelo / Función | Firma | Descripción |
|-----------------|-------|-------------|
| `Autor` | modelo Django | `nombre`, `email` (unique), `biografia` (opcional) |
| `Categoria` | modelo Django | `nombre` (unique) |
| `Libro` | modelo Django | FK → `Autor` (PROTECT), M2M → `Categoria`, campos de catálogo |
| `Prestamo` | modelo Django | FK → `Libro` (CASCADE), `nombre_prestatario`, fechas |
| `Libro.prestamos_activos()` | `() -> int` | Préstamos activos (fecha\_devolucion IS NULL) |
| `Libro.disponibles()` | `() -> int` | `cantidad_total - prestamos_activos()` |
| `Libro.tiene_disponibles()` | `() -> bool` | `True` si hay copias disponibles |
| `libros_por_categoria` | `(nombre: str) -> QuerySet` | Libros de una categoría por nombre |
| `autores_con_mas_de_n_libros` | `(n: int) -> QuerySet` | Autores con más de n libros |
| `libros_sin_disponibilidad` | `() -> QuerySet` | Libros con disponibles == 0 |
| `top_n_libros_mas_prestados` | `(n: int) -> QuerySet` | Top N libros por total de préstamos |

---

## 9) Evaluación automática

Al hacer push a `main`, GitHub Actions:

1. Instala dependencias.
2. Ejecuta `python manage.py migrate`.
3. Ejecuta `python manage.py test -v 2`.
4. Reporta ✅ o ❌ en la pestaña **Actions**.

---

## 10) Troubleshooting rápido

| Problema | Solución |
|----------|----------|
| `pip: command not found` | Usá `python -m pip install ...` |
| `No module named django` | Activá el entorno virtual y corré `pip install -r requirements.txt` |
| `OperationalError: no such table` | Corré `makemigrations` + `migrate` |
| Tests fallan con `NotImplementedError` | Son los `# TODO` que tenés que completar en `models.py` y `queries.py` |
| Actions falla pero local pasa | Revisá que hayas commiteado las migraciones generadas |
| `ModuleNotFoundError: catalogo` | Corré `manage.py` desde la raíz del proyecto |

## 8) Flujo de trabajo recomendado

1. Completá `catalogo/models.py` (Autor, Categoria, Libro, Prestamo + métodos)
2. Corré `python manage.py makemigrations && python manage.py migrate`
3. Corré `python manage.py test catalogo.tests.test_models` y verificá que pasan
4. Completá `catalogo/queries.py` (las 4 funciones)
5. Corré `python manage.py test catalogo.tests.test_queries`
6. Hacé commits significativos durante todo el proceso
7. Push a `main` y verificá GitHub → **Actions**
