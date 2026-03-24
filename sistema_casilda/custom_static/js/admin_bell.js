document.addEventListener("DOMContentLoaded", function() {
    console.log("Admin Bell script loaded.");
    
    // FORCE LIGHT MODE (Runtime)
    document.body.classList.remove('dark-mode');
    document.querySelectorAll('.dark-mode').forEach(el => el.classList.remove('dark-mode'));
    localStorage.setItem('jazzmin-dark-mode', 'false');
    
    // INJECT ABSOLUTE LIGHT THEME CSS
    const style = document.createElement('style');
    style.textContent = `
        /* Override Jazzmin Dark Themes */
        html, body, .wrapper, .content-wrapper, .main-header, .main-sidebar, .card, .content, .info-box, .modal-content, .form-row, .inline-related, .tabular, .module, .submit-row, .content-header {
            background-color: #ffffff !important;
            background: #ffffff !important;
            color: #212529 !important;
        }

        /* Navbar & Sidebar Clean Portal Style */
        .main-header.navbar {
            background: #ffffff !important;
            border-bottom: 3px solid #14855e !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        }
        .main-sidebar {
            background: #ffffff !important;
            border-right: 1px solid #e2e8f0 !important;
        }
        .nav-sidebar .nav-item > .nav-link.active {
            background: #14855e !important;
            color: #ffffff !important;
        }
        .brand-link {
            background: #ffffff !important;
            color: #14855e !important;
            border-bottom: 2px solid #fec107 !important;
        }

        /* Forms & Inputs - High Contrast */
        .form-control, input, select, textarea {
            background-color: #ffffff !important;
            color: #1a202c !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
        }
        label, .card-title, h1, h2, h3 {
            color: #14855e !important;
            font-weight: 700 !important;
        }

        /* Tables & Inlines */
        .table, .tabular, .inline-related {
            background-color: #ffffff !important;
        }
        .table thead th, .tabular th {
            background-color: #f8fafc !important;
            color: #64748b !important;
        }
        .table tbody tr, .tabular tr {
            background-color: #ffffff !important;
            color: #212529 !important;
        }

        /* Animations */
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
