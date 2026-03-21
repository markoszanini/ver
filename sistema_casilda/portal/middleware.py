from django.shortcuts import redirect
from django.contrib.auth import logout


class SeparateAdminSessionMiddleware:
    """
    When a non-staff user (vecino) tries to access /admin/, 
    log them out and redirect to the admin login page so they 
    see a clean login form instead of "not authorized" error.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if request.user.is_authenticated and not request.user.is_staff:
                logout(request)
                return redirect('/admin/login/?next=/admin/')
        
        return self.get_response(request)
