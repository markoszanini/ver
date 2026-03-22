document.addEventListener("DOMContentLoaded", function() {
    console.log("Admin Bell script loaded.");
    fetch("/reclamos/api/unread_count/")
        .then(response => response.json())
        .then(data => {
            console.log("Unread count:", data);
            const navList = document.querySelector("#jazzy-navbar .navbar-nav.ms-auto");
            if (navList) {
                let badgeHTML = "";
                if (data.unread_count > 0) {
                    badgeHTML = `<span class="badge badge-danger navbar-badge" style="position:absolute; top: 0; right: 0;">${data.unread_count}</span>`;
                }
                const bellHTML = `
                <li class="nav-item position-relative me-2">
                    <a class="nav-link" href="/admin/reclamos/mensajereclamo/?leido__exact=0&es_empleado__exact=0" title="Mensajes de Reclamos">
                        <i class="fas fa-bell"></i>
                        ${badgeHTML}
                    </a>
                </li>`;
                navList.insertAdjacentHTML('afterbegin', bellHTML);
            } else {
                console.error("No se encontró el menú superior del Jazzmin.");
            }
        })
        .catch(err => console.error("Error fetching unread reclamos count:", err));
});
