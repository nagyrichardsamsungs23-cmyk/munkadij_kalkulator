"""
Django Admin regisztráció — magyar feliratokkal, kereséssel, szűréssel.
"""

from django.contrib import admin
from .models import (
    WorkCategory, WorkItem, HourlyRate, Multiplier,
    Customer, Estimate, EstimateItem
)


@admin.register(WorkCategory)
class WorkCategoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'name', 'item_count']
    list_display_links = ['name']
    list_editable = ['order']
    search_fields = ['name']
    ordering = ['order', 'name']

    @admin.display(description="Munkafolyamatok")
    def item_count(self, obj):
        return obj.items.count()


class EstimateItemInline(admin.TabularInline):
    model = EstimateItem
    extra = 0
    fields = ['order', 'name', 'quantity', 'unit', 'base_time_hours',
              'multiplier_total', 'calculated_hours', 'calculated_price']
    readonly_fields = ['name', 'unit', 'base_time_hours',
                       'multiplier_total', 'calculated_hours', 'calculated_price']


@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit', 'base_time_hours',
                    'time_minutes_display', 'is_active', 'order']
    list_display_links = ['name']
    list_filter = ['category', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['category__order', 'order', 'name']
    autocomplete_fields = ['category']

    @admin.display(description="Perc")
    def time_minutes_display(self, obj):
        return f"{obj.time_in_minutes():.0f} p"


@admin.register(HourlyRate)
class HourlyRateAdmin(admin.ModelAdmin):
    list_display = ['name', 'formatted_rate', 'valid_from', 'valid_to', 'is_active']
    list_display_links = ['name']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['-valid_from']

    @admin.display(description="Rezsióradíj")
    def formatted_rate(self, obj):
        return f"{obj.hourly_rate:,} Ft/óra".replace(',', ' ')


@admin.register(Multiplier)
class MultiplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'value_display', 'is_active', 'order']
    list_display_links = ['name']
    list_filter = ['type', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name']
    ordering = ['type', 'order']

    @admin.display(description="Érték")
    def value_display(self, obj):
        pct = (float(obj.value) - 1) * 100
        if pct >= 0:
            return f"{obj.value} (+{pct:.0f}%)"
        return f"{obj.value} ({pct:.0f}%)"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'phone', 'email', 'created_at']
    list_display_links = ['name']
    search_fields = ['name', 'city', 'email', 'phone']
    ordering = ['-created_at']


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_display', 'status', 'total_formatted',
                    'total_hours_display', 'created_at']
    list_display_links = ['id']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__name', 'customer_name_override']
    ordering = ['-created_at']
    readonly_fields = ['subtotal_labor', 'subtotal_material', 'total',
                       'total_labor_hours', 'created_at', 'updated_at']
    inlines = [EstimateItemInline]
    autocomplete_fields = ['customer', 'hourly_rate']

    fieldsets = (
        ("Ügyfél adatok", {
            'fields': ['customer', 'customer_name_override']
        }),
        ("Díjak és költségek", {
            'fields': ['hourly_rate', 'travel_fee', 'material_cost',
                       'discount_percent', 'vat_rate']
        }),
        ("Számított összegek", {
            'fields': ['subtotal_labor', 'subtotal_material', 'total']
        }),
        ("Státusz és megjegyzés", {
            'fields': ['status', 'note']
        }),
        ("Időbélyegek", {
            'fields': ['created_at', 'updated_at']
        }),
    )

    @admin.display(description="Végösszeg")
    def total_formatted(self, obj):
        return f"{obj.total:,} Ft".replace(',', ' ')

    @admin.display(description="Össz. munkaóra")
    def total_hours_display(self, obj):
        return f"{obj.total_labor_hours():.2f} ó"


@admin.register(EstimateItem)
class EstimateItemAdmin(admin.ModelAdmin):
    list_display = ['estimate', 'name', 'quantity', 'unit',
                    'calculated_hours', 'calculated_price']
    list_display_links = ['name']
    search_fields = ['name', 'estimate__id']
    ordering = ['estimate', 'order']
