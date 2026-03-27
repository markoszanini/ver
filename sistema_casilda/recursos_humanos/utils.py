import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from django.core.files.base import ContentFile
from django.utils import timezone

class GeneradorReciboPDF:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.header_style = ParagraphStyle(
            'HeaderStyle',
            parent=self.styles['Normal'],
            fontSize=16,
            alignment=1,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        self.normal_style = self.styles['Normal']
        self.bold_style = ParagraphStyle(
            'BoldStyle',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold'
        )

    def generar_pdf_recibo(self, funcionario, liquidacion, detalles):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        elements = []

        # Header
        elements.append(Paragraph("MUNICIPALIDAD DE CASILDA", self.header_style))
        elements.append(Paragraph(f"Recibo de Haberes - Mes: {liquidacion.mes}/{liquidacion.anio}", self.styles['Heading2']))
        elements.append(Spacer(1, 0.5*cm))

        # Empleado Info
        emp_data = [
            [Paragraph(f"<b>Empleado:</b> {funcionario.apellido}, {funcionario.nombre}", self.normal_style), 
             Paragraph(f"<b>Legajo:</b> {funcionario.nro_legajo or funcionario.id_funcionario}", self.normal_style)],
            [Paragraph(f"<b>CUIL:</b> {funcionario.cuil or 'N/A'}", self.normal_style), 
             Paragraph(f"<b>DNI:</b> {funcionario.dni or 'N/A'}", self.normal_style)],
            [Paragraph(f"<b>Área:</b> {funcionario.area.nombre if funcionario.area else 'N/A'}", self.normal_style), 
             Paragraph(f"<b>Rango:</b> {funcionario.get_rango_display()}", self.normal_style)],
            [Paragraph(f"<b>Domicilio:</b> {funcionario.calle or ''} {funcionario.altura or ''}", self.normal_style), 
             Paragraph("", self.normal_style)],
        ]
        t_emp = Table(emp_data, colWidths=[9*cm, 8*cm])
        t_emp.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        elements.append(t_emp)
        elements.append(Spacer(1, 1*cm))

        # Conceptos Table Header
        data = [['Código', 'Concepto', 'Remunerativo', 'Deducciones']]
        
        # Conceptos Remunerativos
        for c in detalles.get('remunerativos', []):
            data.append(['', c['nombre'], f"$ {c['monto']:,.2f}", ''])
            
        # Conceptos Deducciones
        for d in detalles.get('deducciones', []):
            data.append(['', d['nombre'], '', f"$ {d['monto']:,.2f}"])

        # Totales
        data.append(['', '', '', ''])
        data.append(['', 'TOTALES', f"$ {liquidacion.sueldo_bruto:,.2f}", f"$ {liquidacion.total_descuentos:,.2f}"])
        data.append(['', 'NETO A COBRAR', '', f"$ {liquidacion.sueldo_neto:,.2f}"])

        t_concepts = Table(data, colWidths=[2*cm, 8*cm, 3.5*cm, 3.5*cm])
        t_concepts.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('ALIGN', (2,0), (3,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
            ('GRID', (0,0), (-1,-4), 0.5, colors.grey),
            ('LINEBELOW', (0,-2), (-1,-1), 1, colors.black),
            ('FONTNAME', (0,-2), (-1,-1), 'Helvetica-Bold'),
        ]))
        elements.append(t_concepts)
        
        # Footer
        elements.append(Spacer(1, 2*cm))
        elements.append(Paragraph("..................................................", self.header_style))
        elements.append(Paragraph("Firma del Empleado", self.normal_style))

        doc.build(elements)
        pdf_content = buffer.getvalue()
        buffer.close()
        return ContentFile(pdf_content, name=f"recibo_{funcionario.usuario_login}_{liquidacion.mes}_{liquidacion.anio}.pdf")
