document.addEventListener('DOMContentLoaded', function() {
    const $ = window.jQuery || window.django && window.django.jQuery;
    if(!$) return;

    function initCascading(prefix) {
        const $area = $('#id_' + prefix + 'area');
        const $direccion = $('#id_' + prefix + 'direccion');
        const $departamento = $('#id_' + prefix + 'departamento');
        const $division = $('#id_' + prefix + 'division');
        const $subdivision = $('#id_' + prefix + 'subdivision');
        const $seccion = $('#id_' + prefix + 'seccion');
        const $oficina = $('#id_' + prefix + 'oficina');

        if (!$area.length && !$departamento.length) return; // Skip if no relevant fields

        function updateOptionsCustom($select, urlBase, params) {
            let queryParams = $.param(params);
            if (!params || Object.values(params).every(v => !v)) {
                $select.empty().append('<option value="" selected>---------</option>');
                if ($select.hasClass('select2-hidden-accessible')) {
                    $select.trigger('change.select2');
                }
                return;
            }
            $.ajax({
                url: urlBase + '?' + queryParams,
                success: function(data) {
                    const currentVal = $select.val();
                    $select.empty().append('<option value="" selected>---------</option>');
                    data.results.forEach(item => {
                        $select.append(new Option(item.text, item.id));
                    });
                    if ($select.find(`option[value="${currentVal}"]`).length > 0) {
                        $select.val(currentVal);
                    } else {
                        $select.val('');
                    }
                    if ($select.hasClass('select2-hidden-accessible')) {
                        $select.trigger('change.select2');
                    }
                }
            });
        }

        $area.on('change', function() {
            updateOptionsCustom($direccion, '/organigrama/ajax/get_direcciones/', { area_id: $(this).val() });
            updateOptionsCustom($departamento, '/organigrama/ajax/get_departamentos/', { area_id: $(this).val() });
            updateOptionsCustom($oficina, '/organigrama/ajax/get_oficinas/', { area_id: $(this).val() });
        });
        $direccion.on('change', function() {
            updateOptionsCustom($departamento, '/organigrama/ajax/get_departamentos/', { area_id: $area.val(), dir_id: $(this).val() });
        });
        $departamento.on('change', function() {
            updateOptionsCustom($division, '/organigrama/ajax/get_divisiones/', { depto_id: $(this).val() });
            updateOptionsCustom($subdivision, '/organigrama/ajax/get_subdivisiones/', { depto_id: $(this).val() });
            updateOptionsCustom($seccion, '/organigrama/ajax/get_secciones/', { depto_id: $(this).val() });
        });
        $subdivision.on('change', function() {
            updateOptionsCustom($seccion, '/organigrama/ajax/get_secciones/', { depto_id: $departamento.val(), subdiv_id: $(this).val() });
        });
        // The rest of the triggers for Oficinas...
        $division.on('change', function() {});
        $seccion.on('change', function() {});
    }

    // Initialize the multiple form fields prefixes that Expedientes app uses
    initCascading('origen_');
    initCascading('actual_');
    initCascading('destino_');
});
