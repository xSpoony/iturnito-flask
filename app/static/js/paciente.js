// Variables globales (Inicializadas desde el HTML)
let doctorSeleccionado = null; 
let fechaSeleccionada = null;
let horaSeleccionada = null;
let procesando = false;

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    // Inicializa el calendario con un Set vacío si es la primera carga
    generarCalendario(new Set()); 
    configurarBusqueda();
});


// Generar calendario
function generarCalendario(diasDisponibles = new Set()) {
    const container = document.getElementById('calendario-dias');
    container.innerHTML = '';

    const fecha = new Date();
    const primerDia = new Date(fecha.getFullYear(), fecha.getMonth(), 1);
    const ultimoDia = new Date(fecha.getFullYear(), fecha.getMonth() + 1, 0);
    const monthNames = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"];
    document.querySelector('#modal-reserva h4').textContent = monthNames[fecha.getMonth()];


    for (let i = 0; i < primerDia.getDay(); i++) {
        const div = document.createElement('div');
        container.appendChild(div);
    }

    // Días del mes
    for (let dia = 1; dia <= ultimoDia.getDate(); dia++) {
        const fechaDia = new Date(fecha.getFullYear(), fecha.getMonth(), dia);
        const fechaStr = fechaDia.toISOString().split('T')[0];
        const hoy = new Date();
        hoy.setHours(0,0,0,0);

        const esHoy = fechaDia.getTime() === hoy.getTime();
        const esPasado = fechaDia < hoy;
        const estaDisponible = diasDisponibles.has(dia.toString()); 
        const isDisabled = esPasado || !estaDisponible;

        const button = document.createElement('button');
        
        button.className = `w-8 h-8 rounded-lg text-sm font-medium transition-colors ${
            isDisabled ? 
                'text-gray-300 cursor-not-allowed' : 
            esHoy ? 
                'bg-red-500 text-white' : 
                'text-gray-700 hover:bg-gray-100' 
        }`;
        
        button.textContent = dia;
        button.disabled = isDisabled; 

        if (!isDisabled) {
            button.onclick = () => seleccionarFecha(fechaStr, button);
        }

        container.appendChild(button);
    }
}

// Configurar búsqueda
function configurarBusqueda() {
    const input = document.getElementById('busqueda-input');
    input.addEventListener('input', filtrarDoctores);
}

// Filtrar doctores
function filtrarDoctores() {
    const busqueda = document.getElementById('busqueda-input').value.toLowerCase().trim();
    const cards = document.querySelectorAll('.doctor-card');
    const estadoVacio = document.getElementById('estado-vacio');
    let doctoresVisibles = 0;

    cards.forEach(card => {
        const nombre = card.dataset.nombre.toLowerCase();
        const especialidad = card.dataset.especialidad.toLowerCase();

        if (!busqueda || nombre.includes(busqueda) || especialidad.includes(busqueda)) {
            card.style.display = 'block';
            doctoresVisibles++;
        } else {
            card.style.display = 'none';
        }
    });

    if (doctoresVisibles === 0) {
        estadoVacio.style.display = 'block';
    } else {
        estadoVacio.style.display = 'none';
    }
}

// Abrir modal
window.abrirModal = function(doctorId, nombre, especialidad) {
    
    const doctorCard = document.querySelector(`.doctor-card[data-doctor-id="${doctorId}"]`);
    
    let diasDisponiblesStr = doctorCard.dataset.diasDisponibles.replace(/&quot;/g, '"');
    let diasDisponiblesArray = JSON.parse(diasDisponiblesStr); 
    
    const modalidad = doctorCard.dataset.modalidad;
    const precio = parseFloat(doctorCard.dataset.precio) || 0.0;

    doctorSeleccionado = {
        id: doctorId,
        nombre: nombre,
        modalidad: modalidad, 
        precio: precio,       
        diasDisponibles: new Set(diasDisponiblesArray.map(String)) // Asegurar que los días son strings
    }; 
    
    fechaSeleccionada = null;
    horaSeleccionada = null;

    document.getElementById('modal-doctor-info').innerHTML = `
        <span class="text-gray-900">${nombre.toUpperCase()} (${especialidad.toUpperCase()})</span> 
        ${modalidad.toUpperCase()} 
        ${precio > 0 ? ' - $' + precio.toFixed(0) : ''}
    `;

    document.getElementById('disponibilidad-section').style.display = 'none';
    document.getElementById('sin-horarios').style.display = 'none';
    document.getElementById('botones-accion').style.display = 'none';

    generarCalendario(doctorSeleccionado.diasDisponibles); 

    document.getElementById('modal-reserva').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

// Cerrar modal (Necesita ser global para el onclick del HTML)
window.cerrarModal = function() {
    document.getElementById('modal-reserva').style.display = 'none';
    document.body.style.overflow = 'auto';
    doctorSeleccionado = null;
    fechaSeleccionada = null;
    horaSeleccionada = null;
    procesando = false;
}

// Seleccionar fecha
async function seleccionarFecha(fecha, buttonElement) {
    fechaSeleccionada = fecha;
    horaSeleccionada = null;

    // Actualizar estilos del calendario
    document.querySelectorAll('#calendario-dias button').forEach(btn => {
        if (!btn.classList.contains('text-gray-300')) {
            const esHoy = btn.classList.contains('bg-red-500');
            
            if (esHoy && btn !== buttonElement) {
                // Si el botón es el de "hoy" (rojo) Y no es el que clickeé, lo dejo rojo
                btn.className = 'w-8 h-8 rounded-lg text-sm font-medium transition-colors bg-red-500 text-white';
            } else {
                // Para todos los demás, los reseteo
                btn.className = 'w-8 h-8 rounded-lg text-sm font-medium transition-colors text-gray-700 hover:bg-gray-100';
            }
        }
    });

    // Pinto el botón seleccionado (a menos que sea "hoy", que ya está rojo)
    if (!buttonElement.classList.contains('bg-red-500')) {
        buttonElement.className = 'w-8 h-8 rounded-lg text-sm font-medium transition-colors bg-gray-900 text-white';
    }

    // Mostrar loading
    document.getElementById('loading-horarios').style.display = 'block';
    document.getElementById('disponibilidad-section').style.display = 'none';
    document.getElementById('sin-horarios').style.display = 'none';
    document.getElementById('botones-accion').style.display = 'none';

    try {
        // Usar la variable global definida en el HTML
        const url = window.API_URLS.OBTENER_HORARIOS; 
        
        const params = new URLSearchParams({
            doctor_id: doctorSeleccionado.id, 
            fecha: fecha
        });

        const response = await fetch(url + '?' + params.toString());
        const data = await response.json();

        if (response.ok) {
            mostrarHorarios(data.horarios || []);
        } else {
            // Manejar error 400/500 con mensaje del servidor si existe
            throw new Error(data.message || 'Error al cargar horarios');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error al cargar horarios disponibles: ' + error.message, 'error');
    } finally {
        document.getElementById('loading-horarios').style.display = 'none';
    }
}

// Mostrar horarios
function mostrarHorarios(horarios) {
    const container = document.getElementById('horarios-container');
    container.innerHTML = '';

    if (horarios.length === 0) {
        document.getElementById('sin-horarios').style.display = 'block';
        return;
    }

    horarios.forEach(horario => {
        const button = document.createElement('button');
        button.className = 'hora-btn py-3 px-4 rounded-lg text-sm font-medium transition-colors bg-gray-100 hover:bg-gray-200 text-gray-700';
        button.onclick = () => seleccionarHora(horario.hora, button);
        button.textContent = horario.hora;

        container.appendChild(button);
    });

    document.getElementById('disponibilidad-section').style.display = 'block';
    document.getElementById('sin-horarios').style.display = 'none';
}

// Seleccionar hora
function seleccionarHora(hora, buttonElement) {
    horaSeleccionada = hora;

    // Actualizar estilos de horarios
    document.querySelectorAll('.hora-btn').forEach(btn => {
        btn.className = 'hora-btn py-3 px-4 rounded-lg text-sm font-medium transition-colors bg-gray-100 hover:bg-gray-200 text-gray-700';
    });

    buttonElement.className = 'hora-btn py-3 px-4 rounded-lg text-sm font-medium transition-colors bg-gray-900 text-white';

    // Mostrar botones de acción
    document.getElementById('botones-accion').style.display = 'block';
}

// Confirmar reserva (Necesita ser global para el onclick del HTML)
window.confirmarReserva = async function() {
    if (procesando) return;
    if (!doctorSeleccionado || !fechaSeleccionada || !horaSeleccionada) {
        mostrarMensaje('Selecciona una fecha y hora válidas.', 'error');
        return;
    }
    
    procesando = true;
    const btnConfirmar = document.getElementById('btn-confirmar');

    btnConfirmar.innerHTML = `
        <span class="flex items-center justify-center space-x-2">
            <svg class="animate-spin w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <span>Confirmando...</span>
        </span>
    `;
    btnConfirmar.disabled = true;

    try {
        const response = await fetch(window.API_URLS.CONFIRMAR_TURNO, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                doctor_id: doctorSeleccionado.id, 
                fecha: fechaSeleccionada,
                hora: horaSeleccionada
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            mostrarMensaje(data.message, 'success');
            cerrarModal();

            setTimeout(() => {
                window.location.href = window.API_URLS.MIS_TURNOS;
            }, 2000);
        } else {
            mostrarMensaje(data.message || 'Error al reservar el turno (servidor)', 'error');
        }
    } catch (error) {
        console.error('Error de red/reserva:', error);
        mostrarMensaje('Error de red al reservar el turno', 'error');
    } finally {
        procesando = false;
        btnConfirmar.innerHTML = 'CONFIRMAR';
        btnConfirmar.disabled = false;
    }
}

// Mostrar mensaje
function mostrarMensaje(texto, tipo) {
    const container = document.getElementById('mensaje-container');
    const textoEl = document.getElementById('mensaje-texto');
    const iconoSuccess = document.getElementById('icono-success');
    const iconoError = document.getElementById('icono-error');

    textoEl.textContent = texto;

    if (tipo === 'success') {
        container.className = 'bg-green-600 text-white px-4 py-3 rounded-lg shadow-lg border-0';
        iconoSuccess.style.display = 'block';
        iconoError.style.display = 'none';
    } else {
        container.className = 'bg-red-600 text-white px-4 py-3 rounded-lg shadow-lg border-0';
        iconoSuccess.style.display = 'none';
        iconoError.style.display = 'block';
    }

    container.style.display = 'block';

    setTimeout(() => {
        container.style.display = 'none';
    }, 5000);
}

// Event listeners para cerrar modal 
document.addEventListener('click', function(e) {
    const modal = document.getElementById('modal-reserva');
    if (e.target === modal) {
        cerrarModal();
    }
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        cerrarModal();
    }
});
