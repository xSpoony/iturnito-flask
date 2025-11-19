// La lógica de Alpine.js ahora recibe los datos iniciales desde el HTML
function horariosDoctor(configInicial, diasSemanaInicial) {

    // Plantilla de días por defecto si no viene nada de la BD
    const diasPorDefecto = [
        { codigo: 'lunes', nombre: 'Lunes', activo: false, bloques: [{ inicio: '09:00', fin: '17:00' }] },
        { codigo: 'martes', nombre: 'Martes', activo: false, bloques: [{ inicio: '09:00', fin: '17:00' }] },
        { codigo: 'miercoles', nombre: 'Miércoles', activo: false, bloques: [{ inicio: '09:00', fin: '17:00' }] },
        { codigo: 'jueves', nombre: 'Jueves', activo: false, bloques: [{ inicio: '09:00', fin: '17:00' }] },
        { codigo: 'viernes', nombre: 'Viernes', activo: false, bloques: [{ inicio: '09:00', fin: '17:00' }] },
        { codigo: 'sabado', nombre: 'Sábado', activo: false, bloques: [{ inicio: '09:00', fin: '13:00' }] },
        { codigo: 'domingo', nombre: 'Domingo', activo: false, bloques: [{ inicio: '09:00', fin: '13:00' }] }
    ];

    // --- Función de Notificación Centralizada ---
    function mostrarMensaje(texto, tipo) {
        const container = document.getElementById('mensaje-container');
        const textoEl = document.getElementById('mensaje-texto');
        const iconoSuccess = document.getElementById('icono-success');
        const iconoError = document.getElementById('icono-error');

        textoEl.textContent = texto;

        if (tipo === 'success') {
            container.className = 'bg-green-600 text-white px-4 py-3 rounded-lg shadow-lg border-0 mb-4';
            iconoSuccess.style.display = 'block';
            iconoError.style.display = 'none';
        } else {
            container.className = 'bg-red-600 text-white px-4 py-3 rounded-lg shadow-lg border-0 mb-4';
            iconoSuccess.style.display = 'none';
            iconoError.style.display = 'block';
        }

        container.style.display = 'block';

        setTimeout(() => {
            container.style.display = 'none';
        }, 5000);
    }

    return {
        // Usa los datos de Flask o un valor por defecto
        configuracion: configInicial || { duracion_turno: 30, modalidad: "presencial", precio_consulta: 0 },
        diasSemana: diasSemanaInicial && diasSemanaInicial.length > 0 ? diasSemanaInicial : diasPorDefecto,
        excepciones: [],
        nuevaExcepcion: {
            fecha: '',
            motivo: ''
        },
        
        init() {
            window.horariosDoctor = horariosDoctor; 
            this.cargarExcepciones();
        },

        async cargarExcepciones() {
            try {
                const response = await fetch(window.API_URLS_HORARIOS.OBTENER_EXCEPCIONES);
                const data = await response.json();
                if (data.excepciones) {
                    this.excepciones = data.excepciones;
                }
            } catch (e) {
                console.error("Error al cargar excepciones", e);
            }
        },

        agregarBloque(diaIndex) {
            this.diasSemana[diaIndex].bloques.push({ inicio: '09:00', fin: '17:00' });
        },

        eliminarBloque(diaIndex, bloqueIndex) {
            this.diasSemana[diaIndex].bloques.splice(bloqueIndex, 1);
        },

        async guardarConfiguracion() {
            try {
                const response = await fetch(window.API_URLS_HORARIOS.GUARDAR_CONFIGURACION, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.configuracion)
                });
                const data = await response.json();
                if (data.success) {
                    mostrarMensaje('Configuración guardada correctamente', 'success');
                } else {
                    mostrarMensaje(data.message || 'Error al guardar la configuración', 'error');
                }
            } catch (e) {
                console.error("Error al guardar config", e);
                mostrarMensaje('Error de red al guardar la configuración', 'error');
            }
        },

        async guardarHorarios() {
            try {
                const response = await fetch(window.API_URLS_HORARIOS.GUARDAR_HORARIOS, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ horarios: this.diasSemana })
                });
                const data = await response.json();
                if (data.success) {
                    mostrarMensaje('Horarios guardados correctamente', 'success');
                } else {
                    mostrarMensaje(data.message || 'Error al guardar los horarios', 'error');
                }
            } catch (e) {
                console.error("Error al guardar horarios", e);
                mostrarMensaje('Error de red al guardar los horarios', 'error');
            }
        },

        // Las funciones de excepción se dejan, aunque no estén en el HTML proporcionado (por completitud)
        agregarExcepcion() {
            if (this.nuevaExcepcion.fecha) {
                this.excepciones.push({ ...this.nuevaExcepcion });
                this.nuevaExcepcion = { fecha: '', motivo: '' };
                this.guardarExcepciones();
            }
        },

        eliminarExcepcion(index) {
            this.excepciones.splice(index, 1);
            this.guardarExcepciones();
        },

        async guardarExcepciones() {
            try {
                const response = await fetch(window.API_URLS_HORARIOS.GUARDAR_EXCEPCIONES, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ excepciones: this.excepciones })
                });
                const data = await response.json();
                if (data.success) {
                    mostrarMensaje('Excepciones guardadas', 'success');
                } else {
                    mostrarMensaje(data.message || 'Error al guardar las excepciones', 'error');
                }
            } catch (e) {
                console.error("Error al guardar excepciones", e);
                mostrarMensaje('Error de red al guardar las excepciones', 'error');
            }
        }
    }
}
