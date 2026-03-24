document.addEventListener("DOMContentLoaded", function() {
    console.log("Admin Bell script loaded.");
    
    // Add custom animation styles to the head
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse-bell {
            0% { transform: scale(1); }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); }
        }
        .bell-pulse {
            animation: pulse-bell 2s infinite;
            color: #fec107 !important;
        }
        .navbar-badge-premium {
            font-size: 0.6rem;
            font-weight: 800;
            padding: 2px 5px;
            border-radius: 50px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            border: 1px solid white;
        }
    `;
    document.head.appendChild(style);

    fetch("/reclamos/api/unread_count/")
        .then(response => response.json())
        .then(data => {
            const navList = document.querySelector(".navbar-nav.ml-auto") || document.querySelector(".navbar-nav.ms-auto");
            if (navList) {
                let badgeHTML = "";
                let pulseClass = "";
                if (data.unread_count > 0) {
                    badgeHTML = `<span class="badge badge-danger navbar-badge navbar-badge-premium">${data.unread_count}</span>`;
                    pulseClass = "bell-pulse";
                }
                const bellHTML = `
                <li class="nav-item position-relative me-3">
                    <a class="nav-link" href="/admin/reclamos/mensajereclamo/?leido__exact=0&es_empleado__exact=0" title="Mensajes de Reclamos">
                        <i class="fas fa-bell ${pulseClass}"></i>
                        ${badgeHTML}
                    </a>
                </li>`;
                navList.insertAdjacentHTML('afterbegin', bellHTML);
            }
        })
        .catch(err => console.error("Error fetching unread reclamos count:", err));
});
