document.addEventListener('DOMContentLoaded', function () {
    console.log("Script de ubicación automática cargado (Modo Porcentajes)");

    // Coordenadas en PORCENTAJES (0-100) para diseño responsivo
    const coords = {
        'cabeza': [50, 6],
        'cuello': [50, 13],
        'hombro_izquierdo': [32, 18],
        'hombro_derecho': [68, 18],
        'pecho': [50, 23],
        'espalda': [50, 23],
        'codo_izquierdo': [27, 29],
        'codo_derecho': [73, 29],
        'abdomen': [50, 34],
        'mano_izquierda': [21, 42],
        'mano_derecha': [79, 42],
        'pelvis': [50, 44],
        'muslo_izquierdo': [42, 53],
        'muslo_derecho': [58, 53],
        'rodilla_izquierda': [42, 69],
        'rodilla_derecha': [58, 69],
        'pie_izquierdo': [42, 90],
        'pie_derecho': [58, 90]
    };

    function findFields() {
        const nombre = document.querySelector('#id_nombre');
        const left = document.querySelector('#id_left');
        const top = document.querySelector('#id_top');
        return { nombre, left, top };
    }

    function enableField(el) {
        if (!el) return;
        el.removeAttribute('readonly');
        el.readOnly = false;
        el.removeAttribute('disabled');
        el.disabled = false;
    }

    function assignIfPossible(nombreVal) {
        const { left, top } = findFields();
        if (!left || !top) return;

        enableField(left);
        enableField(top);

        const key = (nombreVal || '').trim().toLowerCase();
        if (!key) return;

        if (Object.prototype.hasOwnProperty.call(coords, key)) {
            const [lx, ty] = coords[key];
            left.value = lx;
            top.value = ty;
            // Disparar eventos para que Django Admin detecte el cambio
            ['input', 'change'].forEach(evt => {
                left.dispatchEvent(new Event(evt, { bubbles: true }));
                top.dispatchEvent(new Event(evt, { bubbles: true }));
            });
            console.log(`Asignado: ${key} → left=${lx}%, top=${ty}%`);
        } else {
            console.warn(`Sin coordenadas para: ${key}`);
        }
    }

    function wire() {
        const { nombre, left, top } = findFields();
        if (!nombre || !left || !top) {
            console.warn('Campos no encontrados aún, se seguirá observando…');
            return;
        }

        // Asignar al cargar por si ya viene una selección
        assignIfPossible(nombre.value);

        // Asignar en cada cambio
        nombre.addEventListener('change', function () {
            assignIfPossible(nombre.value);
        });
    }

    // Intento inicial
    wire();

    // Observa cambios en el formulario del admin (render dinámico)
    const adminForm = document.querySelector('form');
    if (adminForm) {
        const obs = new MutationObserver(() => wire());
        obs.observe(adminForm, { childList: true, subtree: true });
    }
});