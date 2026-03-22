document.addEventListener('DOMContentLoaded', function() {
    const $ = window.jQuery || window.django && window.django.jQuery;
    if(!$) return;

    const $tipoActa = $('#id_tipo_acta');
    const $motivo = $('#id_motivo');

    // Clonamos todas las opciones reales en memoria
    let allMotivos = [];
    $motivo.find('option').each(function() {
        allMotivos.push({
            value: $(this).val(),
            text: $(this).text()
        });
    });

    function toggleSection(className, titleText, show) {
        if (show) {
            // Mostrar fieldset nativo
            $(className).show();
            // Mostrar Pestaña/Tab si Jazzmin lo dibujó así
            $('ul.nav-tabs li a').filter(function() {
                return $(this).text().trim() === titleText;
            }).parent().show();
        } else {
            // Ocultar
            $(className).hide();
            $('ul.nav-tabs li a').filter(function() {
                return $(this).text().trim() === titleText;
            }).parent().hide();
        }
    }

    function updateVisibility() {
        const tipo = $tipoActa.val();

        // 1. Ocultar TODO al principio
        toggleSection('.fieldset-animal', 'Datos del Animal', false);
        toggleSection('.fieldset-vehiculo', 'Datos del Vehículo', false);
        toggleSection('.fieldset-inmueble', 'Datos del Inmueble', false);

        // 2. Mostrar solo la pestaña/fieldset que corresponda
        if (tipo === 'ANIMAL') toggleSection('.fieldset-animal', 'Datos del Animal', true);
        if (tipo === 'VEHICULO') toggleSection('.fieldset-vehiculo', 'Datos del Vehículo', true);
        if (tipo === 'INMUEBLE') toggleSection('.fieldset-inmueble', 'Datos del Inmueble', true);

        // 3. Reconstruir Motivos (debe ser vacío por defecto si no hay tipo)
        const currentSel = $motivo.val();
        $motivo.empty();
        
        allMotivos.forEach(function(opt) {
            if (opt.value === '') {
                // Insertar siempre la opción nula (--------)
                $motivo.append(new Option(opt.text, opt.value));
            } else if (tipo && opt.text.startsWith('[' + tipo + ']')) {
                // Solo insertar los motivos que coincidan con la etiqueta [TIPO]
                $motivo.append(new Option(opt.text, opt.value));
            }
            // Si tipo está vacío, no insertamos motivos funcionales.
        });

        // Intentar mantener selección si todavía es válido
        if ($motivo.find("option[value='" + currentSel + "']").length > 0) {
            $motivo.val(currentSel);
        } else {
            $motivo.val('');
        }
        
        // Actualizar UI del plugin Select2 (usado por Jazzmin)
        if ($motivo.hasClass('select2-hidden-accessible')) {
            $motivo.trigger('change.select2');
        }
    }

    if ($tipoActa.length) {
        // Escuchar el evento de cambio
        $tipoActa.on('change', updateVisibility);
        
        // Ejecutar inmediatamente y hacer respaldo 200ms tras inicializar Select2
        updateVisibility();
        setTimeout(updateVisibility, 200);
    }
});
