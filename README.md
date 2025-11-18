# iTurnito - Sistema de Gestión de Turnos Médicos

### 🚨 Advertencias:

  - **El código es de mala calidad** - fue desarrollado con fines puramente académicos
  - **No está optimizado** - prioriza funcionalidad sobre buenas prácticas
  - **No es producción-ready** - NO usar en entornos reales
  - **Sin tests** - no cuenta con pruebas unitarias o de integración
  - **Código vibecodiado** - desarrollado rápidamente sin refactoring

## 📦 Origen del Proyecto

Este repositorio es una **migración de Python/Flask** de un proyecto originalmente escrito en PHP/Laravel.

El repositorio original (Laravel) se puede encontrar aquí:
**[github.com/gonzalo-mv/iturnito](https://www.google.com/search?q=https://github.com/gonzalo-mv/iturnito)**

## 📚 Contexto Académico

Este proyecto fue creado como parte de un trabajo práctico universitario para:

  - Aplicar conceptos de wireframing
  - Implementar interfaces de usuario básicas
  - Demostrar funcionalidad mínima viable

**El sistema funciona**, pero el código no sigue las mejores prácticas de desarrollo.

## 🛠️ Stack Tecnológico (Versión Flask)

  - **Flask** - MicroFramework de Python
  - **SQLAlchemy** - ORM para la base de datos
  - **Flask-Migrate (Alembic)** - Manejo de migraciones
  - **SQLite** - Base de datos local
  - **PostgreSQL** - Base de datos online
  - **Alpine.js** - Framework de JavaScript
  - **Tailwind CSS** - Estilos
  - **Gunicorn** - Servidor WSGI para deploy

## 📋 Funcionalidades

Sistema básico de gestión de turnos médicos que incluye:

  - Registro de pacientes y doctores (y panel de Admin)
  - Gestión de horarios disponibles por parte del doctor
  - Reserva de turnos por parte del paciente
  - Paneles de administración, doctor y paciente.

## 🚀 Instalación (Flask)

1.  **Clonar el repositorio:**

    ```bash
    git clone https://github.com/xSpoony/iturnito-flask.git
    ```

2.  **Crear y activar un entorno virtual:**

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Instalar dependencias de Python:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Instalar dependencias de JS (para Tailwind/Alpine):**

    ```bash
    npm install
    npm run build
    ```

5.  **Ejecutar migraciones de la base de datos:**

    ```bash
    flask db upgrade
    ```

6.  **Iniciar el servidor de Flask:**

    ```bash
    flask run
    ```

## 📂 Estructura de Base de Datos

El sistema cuenta con las siguientes tablas principales:

  - `users` - Usuarios del sistema (Admin, Doctor, Paciente)
  - `pacientes` - Perfil de paciente (vinculado a `users`)
  - `doctores` - Perfil de doctor (vinculado a `users`)
  - `especialidades` - Especialidades médicas
  - `turnos` - Registro de turnos
  - `horarios_disponibles` - Disponibilidad semanal de los doctores
  - `configuracion_horario` - Configuración de turnos por doctor

## ⚡ Notas de Desarrollo

  - **Sin manejo robusto de errores** - El sistema puede fallar en casos edge
  - **Sin validaciones complejas** - Validaciones básicas implementadas
  - **Sin optimización de consultas** - Puede ser lento con muchos datos

## 🎓 Uso Académico

Este código se comparte con fines educativos para mostrar:

  - ❌ Cómo NO escribir código en producción
  - ✅ Cómo lograr funcionalidad rápida para prototipos
  - ✅ Implementación básica de wireframes en **Flask**

## 📝 Licencia

Proyecto académico - Usar bajo tu propio riesgo.

-----

**Recordatorio:** Este código fue desarrollado para cumplir con requisitos académicos específicos. Si buscas ejemplos de buenas prácticas, este NO es el repositorio correcto. 😅
