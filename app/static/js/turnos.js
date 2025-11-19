// window.dayjs debe estar disponible antes de que se ejecute esta sección.
if (typeof dayjs !== 'undefined') {
    dayjs.extend(dayjs_plugin_updateLocale);
    dayjs.updateLocale('en', {
      months: [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
        "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
      ],
      weekdays: [
        "Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"
      ],
      weekdaysShort: ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    });
}


function turnosDoctor() {
    // Usar la variable global para las URLs
    const API_URLS = window.API_URLS_TURNOS; 

    const urlParams = new URLSearchParams(window.location.search);
    const fechaParam = urlParams.get('fecha');

    return {
        vista: urlParams.get('vista') || 'dia',
        fechaActual: fechaParam ? dayjs(fechaParam) : dayjs(),
        filtroEstado: urlParams.get('estado') || 'todos',
        
        // Hacemos las funciones disponibles globalmente para el HTML
        init() {
            window.turnosDoctor = turnosDoctor; 
        },

        fechaAnterior() {
            if (this.vista === 'dia') {
                this.fechaActual = this.fechaActual.subtract(1, 'day');
            } else {
                this.fechaActual = this.fechaActual.subtract(1, 'week');
            }
            this.cargarTurnos();
        },

        fechaSiguiente() {
            if (this.vista === 'dia') {
                this.fechaActual = this.fechaActual.add(1, 'day');
            } else {
                this.fechaActual = this.fechaActual.add(1, 'week');
            }
            this.cargarTurnos();
        },

        cargarTurnos() {
            const params = new URLSearchParams();
            params.set('fecha', this.fechaActual.format('YYYY-MM-DD'));
            params.set('vista', this.vista);
            params.set('estado', this.filtroEstado);
            window.location.search = params.toString();
        },

        async _enviarAccion(urlBase, turnoId, confirmacion, datos = null) {
            if (confirmacion && !confirm(confirmacion)) {
                return;
            }
            const url = urlBase.replace('0', turnoId);
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: datos ? JSON.stringify(datos) : null
                });
                const data = await response.json();
                if (data.success) {
                    location.reload(); // Recargar para reflejar el cambio
                } else {
                    alert(data.message || 'Ocurrió un error.');
                }
            } catch(e) {
                alert('Error de red al realizar la acción.');
            }
        },

        completarTurno(turnoId) {
            this._enviarAccion(API_URLS.COMPLETAR_TURNO, turnoId, '¿Marcar este turno como completado?');
        },

        cancelarTurno(turnoId) {
            this._enviarAccion(API_URLS.CANCELAR_TURNO, turnoId, '¿Cancelar este turno?');
        },

        async guardarNotas(turnoId, notas) {
            try {
                const url = API_URLS.GUARDAR_NOTAS.replace('0', turnoId);
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ notas: notas || '' })
                });
                const data = await response.json();
                if (data.success) {
                    alert('Notas guardadas correctamente');
                } else {
                     alert(data.message || 'Error al guardar notas.');
                }
            } catch (e) {
                alert('Error de red al guardar notas.');
            }
        },

        iniciarVideoLlamada(turnoId) {
            const url = API_URLS.INICIAR_VIDEOLLAMADA.replace('0', turnoId);
            window.open(url, '_blank');
        }
    }
}