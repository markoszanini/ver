document.addEventListener('DOMContentLoaded', function() {
    const $ = window.jQuery || window.django && window.django.jQuery;
    if(!$) return;

    console.log("Organigrama Admin JS v3 Loading...");

    const $area = $('#id_area');
    const $direccion = $('#id_direccion');
    const $departamento = $('#id_departamento');
    const $division = $('#id_division');
    const $subdivision = $('#id_subdivision');
    const $seccion = $('#id_seccion');
    const $oficina = $('#id_oficina');

    function updateOptionsCustom($select, urlBase, params) {
        if (!$select.length) return;
        
        let queryParams = $.param(params);
        console.log("Refreshing select:", $select.attr('id'), "with url:", urlBase, "params:", params);

        $.ajax({
            url: urlBase + '?' + queryParams,
            success: function(data) {
                const currentVal = $select.val();
                $select.empty().append('<option value="" selected>---------</option>');
                if (data.results) {
                    data.results.forEach(item => {
                        $select.append(new Option(item.text, item.id));
                    });
                }
                
                if ($select.find(`option[value="${currentVal}"]`).length > 0) {
                    $select.val(currentVal);
                } else {
                    $select.val('');
                }
                
                if ($select.hasClass('select2-hidden-accessible')) {
                    $select.trigger('change.select2');
                }
            },
            error: function(err) {
                console.error("AJAX Error for", $select.attr('id'), err);
            }
        });
    }

    function refreshDirecciones() {
        updateOptionsCustom($direccion, '/organigrama/ajax/get_direcciones/', { area_id: $area.val() });
    }
    function refreshDepartamentos() {
        updateOptionsCustom($departamento, '/organigrama/ajax/get_departamentos/', { area_id: $area.val(), dir_id: $direccion.val() });
    }
    function refreshDivisiones() {
        updateOptionsCustom($division, '/organigrama/ajax/get_divisiones/', { area_id: $area.val(), depto_id: $departamento.val() });
    }
    function refreshSubdivisiones() {
        updateOptionsCustom($subdivision, '/organigrama/ajax/get_subdivisiones/', { area_id: $area.val(), dir_id: $direccion.val(), depto_id: $departamento.val(), div_id: $division.val() }); 
    }
    function refreshSecciones() {
        updateOptionsCustom($seccion, '/organigrama/ajax/get_secciones/', { area_id: $area.val(), dir_id: $direccion.val(), depto_id: $departamento.val(), div_id: $division.val(), subdiv_id: $subdivision.val() });
    }
    function refreshOficinas() {
        updateOptionsCustom($oficina, '/organigrama/ajax/get_oficinas/', {
            area_id: $area.val(),
            dir_id: $direccion.val(),
            depto_id: $departamento.val(),
            div_id: $division.val(),
            subdiv_id: $subdivision.val(),
            sec_id: $seccion.val()
        });
    }

    $area.on('change', function() {
        refreshDirecciones();         
        refreshDepartamentos();       
        refreshDivisiones();
        refreshSubdivisiones();
        refreshSecciones();
        refreshOficinas();            
    });

    $direccion.on('change', function() {
        refreshDepartamentos();       
        refreshDivisiones();
        refreshSubdivisiones();
        refreshSecciones();
        refreshOficinas();            
    });

    $departamento.on('change', function() {
        refreshDivisiones();          
        refreshSubdivisiones();
        refreshSecciones();           
        refreshOficinas();            
    });

    $division.on('change', function() {
        refreshSubdivisiones();
        refreshSecciones();
        refreshOficinas();            
    });
    
    $subdivision.on('change', function() {
        refreshSecciones();           
        refreshOficinas();            
    });

    $seccion.on('change', function() {
        refreshOficinas();            
    });

    // Limpieza inicial forzada (Pedido del usuario: todos deben empezar con ---------)
    $area.val('').trigger('change.select2');
    $direccion.empty().append('<option value="">---------</option>').val('').trigger('change.select2');
    $departamento.empty().append('<option value="">---------</option>').val('').trigger('change.select2');
    $division.empty().append('<option value="">---------</option>').val('').trigger('change.select2');
    $subdivision.empty().append('<option value="">---------</option>').val('').trigger('change.select2');
    $seccion.empty().append('<option value="">---------</option>').val('').trigger('change.select2');
    $oficina.empty().append('<option value="">---------</option>').val('').trigger('change.select2');

    // Mantenemos el setTimeout pero vacío por si necesitamos habilitar algo más adelante 
    // o para asegurar que el navegador no intente restaurar valores.
    setTimeout(function() {
        console.log("Initial state: Cleaned.");
    }, 100);

    console.log("Organigrama Admin JS v3 Loaded.");
});
