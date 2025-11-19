// Función para mostrar/ocultar contraseña
function togglePassword() {
    const passwordInput = document.getElementById('passwordInput');
    const eyeIcon = document.getElementById('eyeIcon');

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        eyeIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
        `;
    } else {
        passwordInput.type = 'password';
        eyeIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
        `;
    }
}

// Manejo del envío del formulario
document.getElementById('loginForm').addEventListener('submit', function(e) {
    const submitBtn = document.getElementById('submitBtn');
    const submitText = document.getElementById('submitText');

    // Mostrar estado de carga
    submitBtn.disabled = true;
    submitText.textContent = 'Iniciando sesión...';

    setTimeout(() => {
        if (window.location.href === window.location.href) {
            submitBtn.disabled = false;
            submitText.textContent = 'Iniciar Sesión';
        }
    }, 5000);
});

// Validación de inputs
document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('input[required]');

    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value.trim() === '') {
                this.classList.add('border-red-300');
                this.classList.remove('border-gray-200');
            } else {
                this.classList.remove('border-red-300');
                this.classList.add('border-gray-200');
            }
        });

        input.addEventListener('input', function() {
            if (this.classList.contains('border-red-300') && this.value.trim() !== '') {
                this.classList.remove('border-red-300');
                this.classList.add('border-gray-200');
            }
        });
    });
});

// Auto-focus en el primer input
window.addEventListener('load', function() {
    const firstInput = document.querySelector('input[name="email"]');
    if (firstInput) {
        firstInput.focus();
    }
});
