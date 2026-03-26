(function($) {
    if (!$) $ = django.jQuery || jQuery;
    
    $(document).ready(function() {
        console.log("Apicultura Industrial Strength JS loaded (V15)");

        function setVisibility($field, show) {
            var $row = $field.closest('.form-group, .form-row');
            if (!$row.length) return;
            
            if (show) {
                // Forzar visualización con flex para mantener el layout de Jazzmin
                $row.attr('style', 'display: flex !important;');
            } else {
                $row.attr('style', 'display: none !important;');
            }
        }

        function updateAll() {
            // 1. Extracción: forma_pago -> precio_por_kg
            $('select[name*="forma_pago"]').each(function() {
                var $select = $(this);
                var val = ($select.val() || "").toUpperCase();
                var $container = $select.closest('form, fieldset');
                var $field = $container.find('[name*="precio_por_kg"]');
                
                setVisibility($field, val === 'DINERO');
            });

            // 2. Apicultor: usa_sala_extraccion -> extraccion_alter
            $('select[name*="usa_sala_extraccion"]').each(function() {
                var $select = $(this);
                var val = ($select.val() || "").toUpperCase();
                // Soportar 'N' (modelo) y 'NO' (posible normalización de Jazzmin)
                var isNo = (val === 'N' || val === 'NO');
                
                var $container = $select.closest('.inline-related, fieldset, form');
                var $field = $container.find('[name*="extraccion_alter"]');
                
                setVisibility($field, isNo);
            });
        }

        // Listener para cambios
        $(document).on('change', 'select', updateAll);

        // Ejecución inicial y protección contra carga asíncrona
        updateAll();
        setTimeout(updateAll, 500);
        setTimeout(updateAll, 2000);
        
        // Polling (solo si es necesario, pero Jazzmin es muy dinámico)
        setInterval(updateAll, 3000);

        // Soporte para agregado de inlines
        $(document).on('formset:added', updateAll);
    });
})(window.django ? django.jQuery : jQuery);
