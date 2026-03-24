document.addEventListener("DOMContentLoaded", function() {
    console.log("Admin Bell script loaded.");
    
    // FORCE LIGHT MODE (Nuclear Option)
    const forceLight = () => {
        const body = document.body;
        
        // Remove all possible dark classes
        const darkClasses = [
            'dark-mode', 'sidebar-dark-primary', 'sidebar-dark-warning', 
            'sidebar-dark-success', 'sidebar-dark-danger', 'sidebar-dark-info',
            'navbar-dark', 'navbar-black', 'navbar-navy'
        ];
        
        darkClasses.forEach(cls => {
            body.classList.remove(cls);
            document.querySelectorAll('.' + cls).forEach(el => el.classList.remove(cls));
        });

        // Add light classes
        body.classList.add('sidebar-light-primary');
        const navbar = document.querySelector('.main-header.navbar');
        if (navbar) {
            navbar.classList.remove('navbar-dark');
            navbar.classList.add('navbar-light', 'navbar-white');
        }
        
        const sidebar = document.querySelector('.main-sidebar');
        if (sidebar) {
            sidebar.classList.remove('sidebar-dark-primary');
            sidebar.classList.add('sidebar-light-primary');
        }

        localStorage.setItem('jazzmin-dark-mode', 'false');
    };

    forceLight();
    // Run again after a short delay in case Jazzmin JS reapplies them
    setTimeout(forceLight, 500);
    setTimeout(forceLight, 2000);
    
    // INJECT ABSOLUTE LIGHT THEME CSS
    const style = document.createElement('style');
    style.textContent = `
        /* Override Jazzmin Dark Themes with extreme specificity */
        html, body, .wrapper, .content-wrapper, .main-header, .main-sidebar, .card, .content, .info-box, .modal-content, .form-row, .inline-related, .tabular, .module, .submit-row, .content-header {
            background-color: #ffffff !important;
            background: #ffffff !important;
            color: #212529 !important;
        }

        /* Sidebar ABSOULTE LIGHT FORCE */
        .main-sidebar, .main-sidebar *, .sidebar, .sidebar * {
            background-color: #ffffff !important;
            color: #475569 !important;
        }
        
        .main-sidebar .nav-link.active {
            background-color: #14855e !important;
            color: #ffffff !important;
        }

        /* Navbar & Brand */
        .main-header.navbar {
            background: #ffffff !important;
            border-bottom: 3px solid #14855e !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        }
        .brand-link, .brand-link * {
            background: #ffffff !important;
            color: #14855e !important;
            border-bottom: 2px solid #fec107 !important;
        }

        /* Forms & Inputs - High Contrast */
        .form-control, input, select, textarea, .select2-selection {
            background-color: #ffffff !important;
            color: #1a202c !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
        }
        
        /* Buttons - FORCING PORTAL COLORS */
        .btn-primary, .btn-success, .btn-info, .btn-warning {
            background-color: #14855e !important;
            border-color: #14855e !important;
            color: #ffffff !important;
            border-radius: 50px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
        }
        
        .btn-info:hover, .btn-primary:hover {
            background-color: #0a5a3f !important;
            transform: translateY(-2px);
        }

        label, .card-title, h1, h2, h3 {
            color: #14855e !important;
            font-weight: 800 !important;
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
