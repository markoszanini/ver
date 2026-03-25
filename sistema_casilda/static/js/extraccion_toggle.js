function initTogglePago() {
    var $ = window.jQuery || (typeof django !== 'undefined' ? django.jQuery : null);
    if (!$) {
        setTimeout(initTogglePago, 50);
        return;
    }

    console.log("Script de extraccion toggle (Poll) cargado.");

    function toggleFields() {
        var formaPagoSelect = document.getElementById('id_forma_pago');
        if (!formaPagoSelect) return;
        
        var currentVal = formaPagoSelect.value;
        var lastVal = formaPagoSelect.getAttribute('data-last-val');
        
        // Ejecutar si el valor ha cambiado, o si es la primera ejecución (lastVal es nulo)
        if (currentVal === lastVal && currentVal !== null) return;
        formaPagoSelect.setAttribute('data-last-val', currentVal);
        
        // En Django Admin nativo, cada field está envuelto en div.field-<nombre>
        var $precioKgRow = $('.field-precio_por_kg');
        var precioKgInput = document.getElementById('id_precio_por_kg');
        
        if (currentVal === 'DINERO') {
            $precioKgRow.show();
        } else {
            $precioKgRow.hide();
            if (precioKgInput && currentVal !== '') {
                precioKgInput.value = ''; 
            }
        }
    }

    // Polling infalible cada 400ms para evadir Jazzmin/Select2 event blocking
    setInterval(toggleFields, 400);
}

// Iniciar
initTogglePago();
