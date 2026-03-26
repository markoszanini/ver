(function() {
    var AJAX_URL = '/ferias/ajax/subrubros/';

    function initChainedSubrubro() {
        var $ = window.jQuery || (typeof django !== 'undefined' ? django.jQuery : null);
        if (!$) { setTimeout(initChainedSubrubro, 100); return; }

        var rubroSelect = document.getElementById('id_rubro');
        var subrubroSelect = document.getElementById('id_subrubro');
        if (!rubroSelect || !subrubroSelect) return;

        var lastRubroVal = rubroSelect.value;

        function updateSubrubros(rubroId, keepCurrent) {
            var $sub = $(subrubroSelect);
            var currentVal = subrubroSelect.value;

            if (!rubroId) {
                $sub.empty().append(new Option('---------', ''));
                $sub.trigger('change');
                return;
            }

            $.ajax({
                url: AJAX_URL,
                data: { rubro_id: rubroId },
                dataType: 'json',
                success: function(data) {
                    $sub.empty().append(new Option('---------', ''));
                    data.forEach(function(item) {
                        var opt = new Option(item.nombre, item.id);
                        if (keepCurrent && String(item.id) === String(currentVal)) {
                            opt.selected = true;
                        }
                        $sub.append(opt);
                    });
                    $sub.trigger('change');
                }
            });
        }

        // Initial load: if rubro has value populate, otherwise clear to empty
        if (rubroSelect.value) {
            updateSubrubros(rubroSelect.value, true);
        } else {
            // Clear all Django-rendered options so it starts empty
            var $sub = $(subrubroSelect);
            $sub.empty().append(new Option('---------', ''));
            $sub.trigger('change');
        }

        // Polling (infalible contra Jazzmin/Select2)
        setInterval(function() {
            var currentVal = rubroSelect.value;
            if (currentVal !== lastRubroVal) {
                lastRubroVal = currentVal;
                updateSubrubros(currentVal, false);
            }
        }, 400);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initChainedSubrubro);
    } else {
        initChainedSubrubro();
    }
})();
