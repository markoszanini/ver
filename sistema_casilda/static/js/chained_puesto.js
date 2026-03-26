function initChainedPuestos() {
    var $ = window.jQuery || (typeof django !== 'undefined' ? django.jQuery : null);
    
    if (!$) {
        setTimeout(initChainedPuestos, 50);
        return;
    }

    console.log("Script de selects anidados (Poll V6) cargado con éxito.");

    function updatePuestos($rubroSelect) {
        var rubroId = $rubroSelect.val();
        var rubroIdAttr = $rubroSelect.attr('id');
        if (!rubroIdAttr) return;

        var puestoIdAttr = rubroIdAttr.replace('-rubro', '-puesto');
        var $puestoSelect = $('#' + puestoIdAttr);
        
        if (!$puestoSelect.length) return;

        if (rubroId) {
            $.ajax({
                url: '/empleo/ajax/puestos/',
                data: { 'rubro_id': rubroId },
                success: function(data) {
                    var currentSelection = $puestoSelect.val();
                    $puestoSelect.empty();
                    
                    $puestoSelect.append(new Option('---------', '', false, false));
                    
                    var found = false;
                    $.each(data, function(index, item) {
                        var isSelected = (item.id_puesto == currentSelection) || (item.id_puesto == parseInt(currentSelection, 10));
                        if (isSelected) found = true;
                        var newOption = new Option(item.descripcion, item.id_puesto, false, isSelected);
                        $puestoSelect.append(newOption);
                    });
                    
                    if (!found && currentSelection) {
                        $puestoSelect.val('');
                    }
                    
                    $puestoSelect.trigger('change');
                },
                error: function() {
                    console.error('Error cargando puestos para el rubro ' + rubroId);
                }
            });
        } else {
            $puestoSelect.empty();
            $puestoSelect.append(new Option('---------', '', false, false));
            $puestoSelect.trigger('change');
        }
    }

    // Usar polling cada 400ms para evitar CUALQUIER problema de eventos bloqueados por Jazzmin/Select2
    setInterval(function() {
        $('select[id$="-rubro"]').each(function() {
            var $rubroSelect = $(this);
            var currentVal = $rubroSelect.val();
            var lastVal = $rubroSelect.data('last-val');
            
            // Si es la primera vez que lo vemos, inicializamos el valor sin disparar update
            // a menos que tenga valor pre-cargado desde backend (modo edicion).
            if (typeof lastVal === 'undefined') {
                $rubroSelect.data('last-val', currentVal);
                if (currentVal) {
                    updatePuestos($rubroSelect);
                } else {
                    // Inicializar Puesto vacio en nueva fila
                    var puestoIdAttr = $rubroSelect.attr('id').replace('-rubro', '-puesto');
                    var $puestoSelect = $('#' + puestoIdAttr);
                    if ($puestoSelect.children('option').length > 1) {
                        $puestoSelect.empty();
                        $puestoSelect.append(new Option('---------', '', false, false));
                        $puestoSelect.trigger('change');
                    }
                }
                return;
            }

            // Si el valor cambió en esta iteracion de tiempo
            if (currentVal !== lastVal) {
                console.log("Cambio detectado vía Polling: Rubro " + lastVal + " -> " + currentVal);
                $rubroSelect.data('last-val', currentVal);
                updatePuestos($rubroSelect);
            }
        });
    }, 400);

}

initChainedPuestos();
