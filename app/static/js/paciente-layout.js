document.addEventListener('DOMContentLoaded', function() {
    // Agregar indicador de carga para formularios automáticamente
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            
            // Solo si el botón existe y no está ya deshabilitado
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                
                // Reemplazar contenido con Spinner
                submitBtn.innerHTML = `
                    <svg class="animate-spin w-4 h-4 mr-2 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                    </svg>
                    Procesando...
                `;

                // Restaurar después de 10 segundos como medida de seguridad (fallback)
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 10000);
            }
        });
    });

    // 2. Mejorar navegación (Placeholder para lógica futura)
    window.addEventListener('popstate', function(e) {
        // Lógica de navegación si fuera necesaria
    });
});

// Función global para mostrar mensajes (Toast)
window.mostrarMensaje = function(mensaje, tipo = 'info') {
    const container = document.createElement('div');
    container.className = 'fixed top-4 left-1/2 transform -translate-x-1/2 z-50 max-w-sm w-full mx-4';

    const colores = {
        success: 'bg-green-600 border-green-500',
        error: 'bg-red-600 border-red-500',
        warning: 'bg-amber-600 border-amber-500',
        info: 'bg-gray-900 border-gray-800'
    };

    container.innerHTML = `
        <div class="${colores[tipo] || colores.info} text-white px-4 py-3 rounded-lg shadow-lg border">
            <div class="flex items-center space-x-3">
                <p class="font-medium text-sm flex-1">${mensaje}</p>
                <button onclick="this.parentElement.parentElement.parentElement.remove()" class="text-white hover:text-gray-200 flex-shrink-0">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(container);

    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        if (container.parentNode) {
            container.remove();
        }
    }, 5000);
};
