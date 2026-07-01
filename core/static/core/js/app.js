/* ═══════════════════════════════════════
   app.js — Interactividad del sitio
   ═══════════════════════════════════════ */

// ─── Modo oscuro/claro ───
const botonModo = document.getElementById('toggle-modo');
const iconoModo = document.getElementById('icono-modo');

if (botonModo) {
    botonModo.addEventListener('click', function () {
        document.body.classList.toggle('modo-oscuro');
        // Alternar entre modo oscuro y claro
        if (document.body.classList.contains('modo-oscuro')) {
            iconoModo.textContent = '☀️';
            document.cookie = 'modo_oscuro=true; path=/; max-age=31536000';
        } else {
            iconoModo.textContent = '🌙';
            document.cookie = 'modo_oscuro=false; path=/; max-age=31536000';
        }
    });
}

// ─── Modal de detalle de función ───
let modalAbierto = false;

function abrirModal(funcionId) {
    const modal = document.getElementById('modal-funcion');
    const body = document.getElementById('modal-body');
    if (!modal || !body) return;

    modal.style.display = 'flex';
    modalAbierto = true;
    document.body.style.overflow = 'hidden';
    body.innerHTML = '<p class="modal-cargando">Cargando...</p>';

    // Cargar detalle via fetch
    fetch('/funcion/' + funcionId + '/?formato=modal')
        .then(function (res) { return res.text(); })
        .then(function (html) {
            body.innerHTML = html;
        })
        .catch(function () {
            body.innerHTML = '<p class="modal-cargando">Error al cargar la información 😢</p>';
        });
}

function cerrarModal() {
    const modal = document.getElementById('modal-funcion');
    if (!modal) return;
    modal.style.display = 'none';
    modalAbierto = false;
    document.body.style.overflow = '';
}

// Cerrar modal con tecla Escape
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && modalAbierto) {
        cerrarModal();
    }
});

// Cerrar modal al hacer click fuera
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('modal-overlay')) {
        cerrarModal();
    }
});
