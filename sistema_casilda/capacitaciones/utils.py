import os
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.core.files.base import ContentFile

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    s_url = settings.STATIC_URL
    s_root = settings.STATIC_ROOT

    if uri.startswith(s_url):
        path = os.path.join(s_root, uri.replace(s_url, ""))
    else:
        # Fallback for logo_path directly provided in context
        path = uri

    if not os.path.isfile(path):
        # Retry with BASE_DIR/static if static_root is not populated
        path2 = os.path.join(settings.BASE_DIR, 'static', uri.replace(s_url, ""))
        if os.path.isfile(path2):
            return path2
        return uri
    return path

def generate_certificate_pdf(inscripcion):
    """
    Generates a PDF certificate for a finished training course.
    Returns a ContentFile ready to be saved in a FileField.
    """
    template = get_template('capacitaciones/certificado_pdf.html')
    
    # Context for the template
    context = {
        'inscripcion': inscripcion,
        'vecino': inscripcion.vecino.user.get_full_name(),
        'dni': inscripcion.vecino.dni,
        'curso': inscripcion.capacitacion.nombre,
        'fecha': inscripcion.capacitacion.fecha_inicio,
        'area': inscripcion.capacitacion.get_area_responsable_display(),
        'logo_muni': os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_muni_v2.png'),
    }
    
    html = template.render(context)
    result = BytesIO()
    
    # Create PDF with link_callback
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
    
    if not pdf.err:
        filename = f"Certificado_{inscripcion.vecino.user.username}_{inscripcion.capacitacion.id}.pdf"
        return ContentFile(result.getvalue(), name=filename)
    
    return None
