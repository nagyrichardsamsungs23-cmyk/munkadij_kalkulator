"""
Munkadíj Kalkulátor — View-k
============================
"""

from django.shortcuts import render
from django.http import JsonResponse
from decimal import Decimal, ROUND_HALF_UP
from .models import WorkCategory, WorkItem, HourlyRate, Multiplier, Estimate, EstimateItem, Customer


def home(request):
    """Főoldal — gyors statisztikák és navigáció."""
    context = {
        'category_count': WorkCategory.objects.count(),
        'workitem_count': WorkItem.objects.filter(is_active=True).count(),
        'multiplier_count': Multiplier.objects.filter(is_active=True).count(),
        'latest_rate': HourlyRate.objects.filter(is_active=True).first(),
    }
    return render(request, 'kalkulator/home.html', context)


def calculator(request):
    """Kalkulátor oldal — GET: űrlap megjelenítése, POST: számítás."""

    # Mindig szükséges adatok
    categories = WorkCategory.objects.prefetch_related('items').all()
    multipliers = Multiplier.objects.filter(is_active=True)
    hourly_rates = HourlyRate.objects.filter(is_active=True)

    if request.method == 'POST':
        # --- AJAX számítás JSON válasszal ---
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return _calculate_ajax(request)

    context = {
        'categories': categories,
        'multipliers': multipliers,
        'hourly_rates': hourly_rates,
    }
    return render(request, 'kalkulator/calculator.html', context)


def _calculate_ajax(request):
    """AJAX számítás: JSON-ben visszaadja a kalkuláció eredményét."""
    from decimal import Decimal

    # Rezsióradíj
    rate_id = request.POST.get('hourly_rate')
    try:
        rate = HourlyRate.objects.get(id=rate_id, is_active=True)
        hourly_rate = rate.hourly_rate
    except (HourlyRate.DoesNotExist, ValueError):
        rate = HourlyRate.objects.filter(is_active=True).first()
        hourly_rate = rate.hourly_rate if rate else 14000

    # Szorzók
    multiplier_ids = request.POST.getlist('multipliers')
    multiplier_total = Decimal('1.0')
    selected_multipliers = []
    if multiplier_ids:
        mults = Multiplier.objects.filter(id__in=multiplier_ids, is_active=True)
        for m in mults:
            multiplier_total *= m.value
            selected_multipliers.append({'name': m.name, 'value': float(m.value)})

    # Kiszállás, anyag, kedvezmény, ÁFA
    travel_fee = int(request.POST.get('travel_fee', 0) or 0)
    material_cost = int(request.POST.get('material_cost', 0) or 0)
    discount_pct = Decimal(request.POST.get('discount_percent', '0') or '0')
    vat_rate = Decimal(request.POST.get('vat_rate', '27') or '27')

    # Tételek feldolgozása
    items_data = []
    total_hours = Decimal('0')
    total_labor = Decimal('0')

    # A POST-ban a tételek: item_<id>_qty, item_<id>_checked
    for key, value in request.POST.items():
        if key.startswith('item_') and key.endswith('_qty') and value:
            item_id = key.replace('item_', '').replace('_qty', '')
            quantity = int(value)

            # Csak akkor számolunk, ha be van pipálva (vagy ha nincs checkbox, akkor qty > 0)
            checked = request.POST.get(f'item_{item_id}_checked', 'off')
            if checked != 'on' and quantity <= 0:
                continue

            try:
                work_item = WorkItem.objects.get(id=item_id, is_active=True)
            except WorkItem.DoesNotExist:
                continue

            base_time = work_item.base_time_hours
            item_hours = Decimal(str(quantity)) * base_time * multiplier_total
            item_price = item_hours * Decimal(str(hourly_rate))

            # Kerekítés
            item_hours = item_hours.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
            item_price = item_price.quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            total_hours += item_hours
            total_labor += item_price

            items_data.append({
                'id': work_item.id,
                'name': work_item.name,
                'unit': work_item.get_unit_display(),
                'quantity': quantity,
                'base_time': float(base_time),
                'hours': float(item_hours),
                'price': int(item_price),
            })

    # Összesítés
    subtotal = total_labor + Decimal(str(material_cost)) + Decimal(str(travel_fee))
    discount_amount = subtotal * discount_pct / Decimal('100')
    after_discount = subtotal - discount_amount
    total = after_discount * (Decimal('1') + vat_rate / Decimal('100'))
    total = total.quantize(Decimal('1'), rounding=ROUND_HALF_UP)

    result = {
        'success': True,
        'hourly_rate': hourly_rate,
        'hourly_rate_name': rate.name if rate else '—',
        'multipliers': selected_multipliers,
        'multiplier_total': float(multiplier_total),
        'travel_fee': travel_fee,
        'material_cost': material_cost,
        'discount_percent': float(discount_pct),
        'vat_rate': float(vat_rate),
        'items': items_data,
        'total_hours': float(total_hours.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'total_labor': int(total_labor),
        'subtotal': int(subtotal),
        'discount_amount': int(discount_amount),
        'total': int(total),
    }

    return JsonResponse(result)


def save_estimate(request):
    """Ajánlat mentése (AJAX POST)."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Csak POST metódus'})

    try:
        data = request.POST

        # Rezsióradíj
        rate_id = data.get('hourly_rate')
        rate = HourlyRate.objects.get(id=rate_id, is_active=True)

        # Ügyfél adatok
        customer_name = data.get('customer_name', '').strip()
        customer_phone = data.get('customer_phone', '').strip()
        customer_email = data.get('customer_email', '').strip()
        customer_address = data.get('customer_address', '').strip()
        project_note = data.get('project_note', '').strip()

        # Költség adatok
        travel_fee = int(data.get('travel_fee', 0) or 0)
        material_cost = int(data.get('material_cost', 0) or 0)
        discount_pct = Decimal(data.get('discount_percent', '0') or '0')
        vat_rate = Decimal(data.get('vat_rate', '27') or '27')

        # Szorzók
        multiplier_ids = data.getlist('multipliers')
        mult_total = Decimal('1.0')
        if multiplier_ids:
            for mid in multiplier_ids:
                try:
                    m = Multiplier.objects.get(id=mid, is_active=True)
                    mult_total *= m.value
                except Multiplier.DoesNotExist:
                    pass

        # Ügyfél
        customer = None
        if customer_name:
            customer, _ = Customer.objects.get_or_create(
                name=customer_name,
                phone=customer_phone,
                defaults={
                    'email': customer_email,
                    'address': customer_address,
                    'note': project_note,
                }
            )

        # Tételek és számítás
        total_labor = 0
        total_hours_calc = Decimal('0')
        estimate_items = []

        for key, value in data.items():
            if key.startswith('item_') and key.endswith('_qty') and value:
                item_id = key.replace('item_', '').replace('_qty', '')
                quantity = int(value)

                checked = data.get(f'item_{item_id}_checked', 'off')
                if checked != 'on' and quantity <= 0:
                    continue

                try:
                    wi = WorkItem.objects.get(id=item_id, is_active=True)
                except WorkItem.DoesNotExist:
                    continue

                item_hours = Decimal(str(quantity)) * wi.base_time_hours * mult_total
                item_price_raw = item_hours * Decimal(str(rate.hourly_rate))
                item_hours = item_hours.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
                item_price = int(item_price_raw.quantize(Decimal('1'), rounding=ROUND_HALF_UP))

                total_labor += item_price
                total_hours_calc += item_hours

                estimate_items.append(EstimateItem(
                    work_item=wi,
                    name=wi.name,
                    unit=wi.get_unit_display(),
                    quantity=quantity,
                    base_time_hours=wi.base_time_hours,
                    multiplier_total=mult_total,
                    calculated_hours=item_hours,
                    calculated_price=item_price,
                    order=len(estimate_items) + 1,
                ))

        # Végösszeg
        subtotal = total_labor + material_cost + travel_fee
        discount_amount = int(subtotal * discount_pct / 100)
        after_discount = subtotal - discount_amount
        total = int(after_discount * (1 + vat_rate / 100))

        # Ajánlat mentése
        estimate = Estimate.objects.create(
            customer=customer,
            customer_name_override=customer_name if not customer else '',
            hourly_rate=rate,
            travel_fee=travel_fee,
            material_cost=material_cost,
            discount_percent=discount_pct,
            vat_rate=vat_rate,
            subtotal_labor=total_labor,
            subtotal_material=material_cost,
            total=total,
            note=project_note,
            status='draft',
        )

        for ei in estimate_items:
            ei.estimate = estimate
        EstimateItem.objects.bulk_create(estimate_items)

        return JsonResponse({
            'success': True,
            'estimate_id': estimate.id,
            'total': total,
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
