from django.shortcuts import render
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime
from .models import Extraccion

@staff_member_required
def dashboard_apicultura(request):
    return render(request, 'apicultura/dashboard.html')

@staff_member_required
def generar_informe(request):
    if request.method == 'POST':
        desde = request.POST.get('desde')
        hasta = request.POST.get('hasta')
        tipo_pago = request.POST.get('tipo_pago')

        if not desde or not hasta or not tipo_pago:
            return render(request, 'apicultura/formulario_informe.html', {'error': 'Por favor complete todos los campos.'})

        d_desde = datetime.strptime(desde, '%Y-%m-%d').date()
        d_hasta = datetime.strptime(hasta, '%Y-%m-%d').date()

        queryset = Extraccion.objects.filter(
            fecha_extraccion__gte=d_desde,
            fecha_extraccion__lte=d_hasta,
            forma_pago=tipo_pago
        ).order_by('id_extraccion')

        if not queryset.exists():
            return render(request, 'apicultura/formulario_informe.html', {'error': 'No se encontraron extracciones en ese rango de fechas para el tipo de pago.'})

        datos_extracciones = []
        totales = {
            'sum_kg': 0.0, 'sum_bruto': 0.0, 'sum_10': 0.0,
            'sum_serv_ext': 0.0, 'sum_serv_mant': 0.0, 'sum_muni': 0.0
        }

        for e in queryset:
            dic = {
                'id_extraccion': e.id_extraccion,
                'apicultor': e.apicultor.nombre,
                'total_kg': float(e.total_kg or 0),
            }
            totales['sum_kg'] += dic['total_kg']

            liq_total = e.liquidaciones.filter(tipo_concepto='TOTAL').first()
            liq_ext = e.liquidaciones.filter(tipo_concepto='SERV_EXT').first()
            liq_mant = e.liquidaciones.filter(tipo_concepto='SERV_MANT').first()
            liq_muni = e.liquidaciones.filter(tipo_concepto='MUNICIPALIDAD').first()

            if tipo_pago == 'DINERO':
                dic['precio_por_kg'] = float(e.precio_por_kg or 0)
                dic['total_bruto'] = dic['total_kg'] * dic['precio_por_kg']
                dic['pago_10'] = float(liq_total.importe_9_porciento if liq_total and liq_total.importe_9_porciento else 0)
                dic['servicio_ext'] = float(liq_ext.importe_9_porciento if liq_ext and liq_ext.importe_9_porciento else 0)
                dic['servicio_mant'] = float(liq_mant.importe_9_porciento if liq_mant and liq_mant.importe_9_porciento else 0)
                dic['municipalidad'] = float(liq_muni.importe_9_porciento if liq_muni and liq_muni.importe_9_porciento else 0)

                totales['sum_bruto'] += dic['total_bruto']
                totales['sum_10'] += dic['pago_10']
                totales['sum_serv_ext'] += dic['servicio_ext']
                totales['sum_serv_mant'] += dic['servicio_mant']
                totales['sum_muni'] += dic['municipalidad']
            else:
                dic['servicio_ext'] = float(liq_ext.kg_9_porciento if liq_ext and liq_ext.kg_9_porciento else 0)
                dic['servicio_mant'] = float(liq_mant.kg_9_porciento if liq_mant and liq_mant.kg_9_porciento else 0)
                dic['municipalidad'] = float(liq_muni.kg_9_porciento if liq_muni and liq_muni.kg_9_porciento else 0)

                totales['sum_serv_ext'] += dic['servicio_ext']
                totales['sum_serv_mant'] += dic['servicio_mant']
                totales['sum_muni'] += dic['municipalidad']

            datos_extracciones.append(dic)

        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://sistema-local/validar-acta?tipo={tipo_pago}&desde={d_desde.strftime('%Y%m%d')}&hasta={d_hasta.strftime('%Y%m%d')}"

        context = {
            'tipo_pago': tipo_pago,
            'desde': d_desde,
            'hasta': d_hasta,
            'extracciones': datos_extracciones,
            'totales': totales,
            'qr_url': qr_url,
            'app_user': request.user.username if request.user.is_authenticated else 'Desconocido',
        }
        return render(request, "admin/acta_balance.html", context)

    return render(request, 'apicultura/formulario_informe.html')
