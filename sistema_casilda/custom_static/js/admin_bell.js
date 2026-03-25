document.addEventListener("DOMContentLoaded", function() {
    console.log("Admin Bell script loaded.");
    
    // FORCE LIGHT MODE (Nuclear Option v2 - BS5 Theme Neutralizer)
    const forceLight = () => {
        document.documentElement.setAttribute('data-bs-theme', 'light');
        document.documentElement.style.colorScheme = 'light';
        
        const body = document.body;
        const darkClasses = [
            'dark-mode', 'sidebar-dark-primary', 'sidebar-dark-warning', 
            'sidebar-dark-success', 'sidebar-dark-danger', 'sidebar-dark-info',
            'navbar-dark', 'navbar-black', 'navbar-navy'
        ];
        
        darkClasses.forEach(cls => {
            body.classList.remove(cls);
            document.querySelectorAll('.' + cls).forEach(el => el.classList.remove(cls));
        });

        // Add light classes to main containers
        body.classList.add('sidebar-light-primary');
        
        const sidebar = document.querySelector('.main-sidebar');
        if (sidebar) {
            sidebar.classList.remove('sidebar-dark-primary');
            sidebar.classList.add('sidebar-light-primary');
            sidebar.style.backgroundColor = "#ffffff";
        }

        const navbar = document.querySelector('.main-header.navbar');
        if (navbar) {
            navbar.classList.remove('navbar-dark');
            navbar.classList.add('navbar-light', 'navbar-white');
            navbar.style.backgroundColor = "#1E7F5C";
        }

        // Specific Brand & User Panel Fix
        document.querySelectorAll('.brand-link, .user-panel').forEach(block => {
            block.style.backgroundColor = "#ffffff";
            block.classList.remove('sidebar-dark-primary');
        });

        localStorage.setItem('jazzmin-theme-mode', 'light');
    };

    forceLight();
    // Repeating to combat Jazzmin's internal state restoration
    setInterval(forceLight, 1000); 
    
    // INJECT CRM LIGHT THEME CSS
    const style = document.createElement('style');
    style.textContent = `
        /* Overrides para Admin Casilda CRM (Nuclear White) */
        .main-sidebar, .main-sidebar::before, .sidebar, .brand-link, .user-panel {
            background-color: #ffffff !important;
            border-right: 1px solid #E5E7EB !important;
        }

        .brand-link {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border-bottom: 2px solid #F2B705 !important;
            padding: 1.2rem 0.5rem !important;
            min-height: 80px !important;
        }

        .brand-link img {
            max-height: 55px !important;
            width: auto !important;
        }

        .user-panel {
            border-bottom: 1px solid #E5E7EB !important;
            padding: 18px 10px !important;
            display: flex !important;
            justify-content: center !important;
        }

        .user-panel .info a {
            color: #1E7F5C !important;
            font-weight: 800 !important;
            font-size: 1.1rem !important;
        }

        .nav-sidebar .nav-link {
            color: #495057 !important;
        }

        .nav-sidebar .nav-link i {
            color: #1E7F5C !important;
        }

        /* Buttons CRM */
        .btn-primary, .btn-success, .btn-info {
            background-color: #1E7F5C !important;
            border-color: #1E7F5C !important;
            color: #ffffff !important;
            border-radius: 8px !important;
        }

        .btn-warning, .add-row a {
            background-color: #F2B705 !important;
            border-color: #F2B705 !important;
            color: #1F2937 !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
        }

        /* Inputs Contrast */
        .form-control, input, select, textarea {
            background-color: #ffffff !important;
            color: #1a202c !important;
            border: 1px solid #E5E7EB !important;
        }

        /* Animations */
        @keyframes pulse-bell {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        .bell-pulse {
            animation: pulse-bell 2s infinite;
            color: #F2B705 !important;
        }
        .navbar-badge-premium {
            background-color: #F2B705 !important;
            color: #1F2937 !important;
            font-weight: 800;
            border-radius: 50px;
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
                    badgeHTML = `<span class="badge badge-warning navbar-badge navbar-badge-premium">${data.unread_count}</span>`;
                    pulseClass = "bell-pulse";
                }
                const bellHTML = `
                <li class="nav-item position-relative me-3">
                    <a class="nav-link" href="/admin/reclamos/mensajereclamo/?leido__exact=0&es_empleado__exact=0" title="Mensajes de Reclamos" style="color:white !important;">
                        <i class="fas fa-bell ${pulseClass}"></i>
                        ${badgeHTML}
                    </a>
                </li>`;
                navList.insertAdjacentHTML('afterbegin', bellHTML);
            }
        })
        .catch(err => console.error("Error fetching unread reclamos count:", err));
});
