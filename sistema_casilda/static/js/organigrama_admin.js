document.addEventListener('DOMContentLoaded', function() {
    const $ = window.jQuery || window.django && window.django.jQuery;
    if(!$) return;

    // ----- LOGICA PARA PESTAÑAS (TABS) -----
    // Buscar los fieldsets usando las clases inyectadas en admin.py
    const $fieldsetLugar = $('.tab-lugar').closest('fieldset');
    const $fieldsetRol = $('.tab-rol').closest('fieldset');

    const fieldsets = [
        { id: 'tab_lugar', title: '1. Lugar de Trabajo', el: $fieldsetLugar },
        { id: 'tab_rol', title: '2. Rol Designado', el: $fieldsetRol }
    ];

    if ($fieldsetLugar.length && $fieldsetRol.length) {
        // Crear nav tabs
        const $ul = $('<ul class="nav nav-tabs mb-4 mt-2" role="tablist"></ul>');
        
        fieldsets.forEach(function(fs, i) {
            const activeClass = i === 0 ? 'active' : '';
            const $li = $(`<li class="nav-item">
                <a class="nav-link ${activeClass}" data-toggle="tab" href="#${fs.id}" style="cursor: pointer; font-size: 1.1em;">${fs.title}</a>
            </li>`);
            $ul.append($li);
            
            // Transformar fieldset en tab-pane envolviendolo en un div oculto/visible
            fs.el.wrap(`<div class="tab-pane ${i === 0 ? 'active' : ''}" id="${fs.id}" style="${i === 0 ? '' : 'display:none;'}"></div>`);
            
            // Ocultar titulo original del fieldset (h2) para no repetirlo
            fs.el.find('h2').hide();
        });

        // Insertar Pestañas antes del primer bloque
        $ul.insertBefore($('#' + fieldsets[0].id));

        // Activar control al hacer click
        $ul.find('a').on('click', function(e) {
            e.preventDefault();
            $ul.find('a').removeClass('active');
            $(this).addClass('active');
            
            $('.tab-pane').hide().removeClass('active');
            $($(this).attr('href')).show().addClass('active');
        });
    }

    // ----- LOGICA AJAX PARA DESPLEGABLES ORGÁNICOS -----
    const $area = $('#id_area');
    const $direccion = $('#id_direccion');
    const $departamento = $('#id_departamento');
    const $division = $('#id_division');
    const $subdivision = $('#id_subdivision');
    const $seccion = $('#id_seccion');
    const $oficina = $('#id_oficina');

    // Función que contacta al backend devolviendo JSON para armar el form dinámico
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
                
                // Si el item previo sigue activo tras el ajax, conservarlo
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

    // Funciones específicas para actualizar cada nivel
    function refreshDirecciones() {
        updateOptionsCustom($direccion, '/organigrama/ajax/get_direcciones/', { area_id: $area.val() });
    }
    function refreshDepartamentos() {
        updateOptionsCustom($departamento, '/organigrama/ajax/get_departamentos/', { area_id: $area.val(), dir_id: $direccion.val() });
    }
    function refreshDivisiones() {
        updateOptionsCustom($division, '/organigrama/ajax/get_divisiones/', { depto_id: $departamento.val() });
    }
    function refreshSubdivisiones() {
        updateOptionsCustom($subdivision, '/organigrama/ajax/get_subdivisiones/', { depto_id: $departamento.val() }); 
    }
    function refreshSecciones() {
        updateOptionsCustom($seccion, '/organigrama/ajax/get_secciones/', { depto_id: $departamento.val(), subdiv_id: $subdivision.val() });
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

    // Eventos (Parent Items) dictados por APEX
    $area.on('change', function() {
        refreshDirecciones();         
        refreshDepartamentos();       
        refreshOficinas();            
    });

    $direccion.on('change', function() {
        refreshDepartamentos();       
        refreshOficinas();            
    });

    $departamento.on('change', function() {
        refreshDivisiones();          
        refreshSecciones();           
        refreshOficinas();            
    });

    $division.on('change', function() {
        refreshSubdivisiones();       
        refreshOficinas();            
    });
    
    $subdivision.on('change', function() {
        refreshSecciones();           
        refreshOficinas();            
    });

    $seccion.on('change', function() {
        refreshOficinas();            
    });
});
