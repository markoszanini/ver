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
        apicultor_id = request.POST.get('apicultor')

        if not desde or not hasta:
            from .models import Apicultor
            apicultores = Apicultor.objects.filter(estado='Activo')
            return render(request, 'apicultura/formulario_informe.html', {
                'error': 'Por favor complete las fechas.',
                'apicultores': apicultores
            })

        try:
            d_desde = datetime.strptime(desde, '%Y-%m-%d').date()
            d_hasta = datetime.strptime(hasta, '%Y-%m-%d').date()

            # Query general
            base_queryset = Extraccion.objects.filter(
                fecha_extraccion__gte=d_desde,
                fecha_extraccion__lte=d_hasta
            )
            if apicultor_id:
                base_queryset = base_queryset.filter(apicultor_id=apicultor_id)
            
            # Separar por tipo de pago
            qs_dinero = base_queryset.filter(forma_pago='DINERO').order_by('id_extraccion')
            qs_especie = base_queryset.filter(forma_pago='ESPECIE').order_by('id_extraccion')

            def process_queryset(qs, tipo):
                result = []
                totals = {
                    'sum_kg': 0.0, 'sum_bruto': 0.0, 'sum_retencion': 0.0,
                    'sum_serv_ext': 0.0, 'sum_serv_mant': 0.0, 'sum_muni': 0.0
                }
                for e in qs:
                    liq_total = e.liquidaciones.filter(tipo_concepto='TOTAL').first()
                    liq_ext = e.liquidaciones.filter(tipo_concepto='SERV_EXT').first()
                    liq_mant = e.liquidaciones.filter(tipo_concepto='SERV_MANT').first()
                    liq_muni = e.liquidaciones.filter(tipo_concepto='MUNICIPALIDAD').first()

                    dic = {
                        'nro_consecutivo': e.nro_consecutivo or f"#{e.id_extraccion}",
                        'apicultor': e.apicultor.nombre,
                        'total_kg': float(e.total_kg or 0),
                        'precio_por_kg': float(e.precio_por_kg or 0),
                    }
                    
                    if tipo == 'DINERO':
                        dic['total_bruto'] = dic['total_kg'] * dic['precio_por_kg']
                        dic['pago_10'] = float(liq_total.importe_retencion if liq_total and liq_total.importe_retencion else 0)
                        dic['servicio_ext'] = float(liq_ext.importe_retencion if liq_ext and liq_ext.importe_retencion else 0)
                        dic['servicio_mant'] = float(liq_mant.importe_retencion if liq_mant and liq_mant.importe_retencion else 0)
                        dic['municipalidad'] = float(liq_muni.importe_retencion if liq_muni and liq_muni.importe_retencion else 0)
                    else:
                        dic['pago_10'] = float(liq_total.kg_retencion if liq_total and liq_total.kg_retencion else 0)
                        dic['servicio_ext'] = float(liq_ext.kg_retencion if liq_ext and liq_ext.kg_retencion else 0)
                        dic['servicio_mant'] = float(liq_mant.kg_retencion if liq_mant and liq_mant.kg_retencion else 0)
                        dic['municipalidad'] = float(liq_muni.kg_retencion if liq_muni and liq_muni.kg_retencion else 0)

                    totals['sum_kg'] += dic['total_kg']
                    if tipo == 'DINERO': totals['sum_bruto'] += dic['total_bruto']
                    totals['sum_retencion'] += dic['pago_10']
                    totals['sum_serv_ext'] += dic['servicio_ext']
                    totals['sum_serv_mant'] += dic['servicio_mant']
                    totals['sum_muni'] += dic['municipalidad']
                    result.append(dic)
                return result, totals

            data_dinero, totals_dinero = process_queryset(qs_dinero, 'DINERO')
            data_especie, totals_especie = process_queryset(qs_especie, 'ESPECIE')

            if not data_dinero and not data_especie:
                from .models import Apicultor
                apicultores = Apicultor.objects.filter(estado='Activo')
                return render(request, 'apicultura/formulario_informe.html', {
                    'error': 'No se encontraron extracciones en el período seleccionado.',
                    'apicultores': apicultores
                })

            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://sistema-local/validar-acta?desde={d_desde.strftime('%Y%m%d')}&hasta={d_hasta.strftime('%Y%m%d')}"

            context = {
                'desde': d_desde,
                'hasta': d_hasta,
                'data_dinero': data_dinero,
                'totals_dinero': totals_dinero,
                'data_especie': data_especie,
                'totals_especie': totals_especie,
                'qr_url': qr_url,
                'app_user': request.user.username if request.user.is_authenticated else 'Desconocido',
            }
            return render(request, "admin/acta_balance.html", context)
        except Exception as e:
            from .models import Apicultor
            apicultores = Apicultor.objects.filter(estado='Activo')
            return render(request, 'apicultura/formulario_informe.html', {
                'error': f'Error al generar el informe: {str(e)}',
                'apicultores': apicultores
            })

    from .models import Apicultor
    apicultores = Apicultor.objects.filter(estado='Activo')
    return render(request, 'apicultura/formulario_informe.html', {'apicultores': apicultores})
