document.addEventListener('DOMContentLoaded', function () {
    console.log("Script de ubicación automática cargado");

    const coords = {
        cabeza: [270, 40],
        cuello: [270, 90],
        hombro_izquierdo: [220, 120],
        hombro_derecho: [320, 120],
        codo_izquierdo: [200, 180],
        codo_derecho: [340, 180],
        mano_izquierda: [180, 240],
        mano_derecha: [360, 240],
        espalda: [270, 160],
        pecho: [270, 140],
        abdomen: [270, 200],
        pelvis: [270, 250],
        muslo_izquierdo: [240, 300],
        muslo_derecho: [300, 300],
        rodilla_izquierda: [240, 370],
        rodilla_derecha: [300, 370],
        pie_izquierdo: [240, 460],
        pie_derecho: [300, 460]
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
            // dispara eventos para que el admin registre cambios
            ['input', 'change'].forEach(evt => {
                left.dispatchEvent(new Event(evt, { bubbles: true }));
                top.dispatchEvent(new Event(evt, { bubbles: true }));
            });
            console.log(`Asignado: ${key} → left=${lx}, top=${ty}`);
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

    // Hard refresh puede ser necesario si el navegador cachea estáticos
    // Sugerencia: Ctrl+F5 si sigue sin reflejar los cambios.
});
