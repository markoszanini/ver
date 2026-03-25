/* Candelaria Chatbot Logic */

document.addEventListener('DOMContentLoaded', function() {
    const trigger = document.getElementById('bee-trigger');
    const window = document.getElementById('chat-window');
    const closeBtn = document.getElementById('close-chat');
    const chatBody = document.getElementById('chat-body');
    const badge = document.getElementById('chat-badge');
    const typing = document.getElementById('typing-indicator');

    // Tooltip/Badge activation after 5 seconds to grab attention
    setTimeout(() => {
        if (!window.classList.contains('active')) {
            badge.style.display = 'flex';
        }
    }, 5000);

    // Toggle Chat
    trigger.addEventListener('click', () => {
        window.classList.toggle('active');
        badge.style.display = 'none';
    });

    closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        window.classList.remove('active');
    });

    // Handle Options
    chatBody.addEventListener('click', (e) => {
        if (e.target.classList.contains('option-chip')) {
            const action = e.target.getAttribute('data-action');
            handleAction(action, e.target.innerText);
        }
    });

    function handleAction(action, label) {
        // Add User Message
        addMessage(label, 'user');
        
        // Show Typing
        typing.style.display = 'block';
        chatBody.scrollTop = chatBody.scrollHeight;

        // Response Logic
        setTimeout(() => {
            typing.style.display = 'none';
            let response = "";
            let options = [];

            switch(action) {
                case 'telefonos':
                    response = "Aquí tenés los números más importantes: <br><br> 📞 <strong>Hospital:</strong> 107 / 422111 <br> 📞 <strong>Policía:</strong> 911 / 422222 <br> 📞 <strong>Municipalidad:</strong> 422001 (Lunes a Viernes 7 a 13hs)";
                    break;
                case 'direcciones':
                    response = "Estamos para ayudarte en: <br><br> 📍 <strong>Palacio Municipal:</strong> Casado 2231 <br> 📍 <strong>Centro de Gestión:</strong> Bv. Lisandro de la Torre y Sargento Cabral <br> 📍 <strong>Tribunal de Faltas:</strong> Tucumán 2145";
                    break;
                case 'vencimientos':
                    response = "Recordá que las Tasas Municipales suelen vencer los días 10 de cada mes. Podés consultar tu deuda actual en la sección <strong>Tasa e Impuestos</strong> de tu panel.";
                    break;
                case 'tramites':
                    response = "¿Qué trámite necesitás hacer? <br><br> Podés iniciar un <strong>Reclamo</strong> desde el botón correspondiente en tu panel, o consultar tu <strong>Expediente</strong> para ver cómo avanza tu gestión.";
                    break;
                case 'reset':
                    response = "¡Claro! ¿Qué más necesitás saber? 🐝";
                    options = ['telefonos', 'direcciones', 'vencimientos', 'tramites'];
                    break;
                default:
                    response = "Lo siento, todavía estoy aprendiendo. ¿Te gustaría intentar con otra opción?";
            }

            addMessage(response, 'bot');
            
            // Add "Back" or "Reset" options
            if (action !== 'reset') {
                 addOptions(['reset']);
            } else {
                 addOptions(options);
            }
            
            chatBody.scrollTop = chatBody.scrollHeight;
        }, 1000);
    }

    function addMessage(text, side) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-msg msg-${side} animate-up`;
        msgDiv.innerHTML = text;
        chatBody.appendChild(msgDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function addOptions(actions) {
        const optionsDiv = document.createElement('div');
        optionsDiv.className = 'chat-options animate-up';
        
        actions.forEach(action => {
            const chip = document.createElement('div');
            chip.className = 'option-chip';
            chip.setAttribute('data-action', action);
            
            switch(action) {
                case 'telefonos': chip.innerText = "📞 Teléfonos"; break;
                case 'direcciones': chip.innerText = "📍 Direcciones"; break;
                case 'vencimientos': chip.innerText = "📅 Vencimientos"; break;
                case 'tramites': chip.innerText = "💬 Trámites"; break;
                case 'reset': chip.innerText = "🔄 Volver al inicio"; break;
            }
            optionsDiv.appendChild(chip);
        });
        
        chatBody.appendChild(optionsDiv);
    }
});
