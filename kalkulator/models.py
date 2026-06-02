"""
Munkadíj Kalkulátor — modellek
================================
Villanyszerelési munkafolyamatok normaidő-alapú díjkalkulációja.

Táblák:
  1. WorkCategory   — Munkakategóriák
  2. WorkItem       — Munkafolyamatok (normaidővel)
  3. HourlyRate     — Rezsióradíjak (verziózva)
  4. Multiplier     — Szorzók (nehézség, sürgősség, stb.)
  5. Customer       — Ügyfelek
  6. Estimate       — Ajánlatok
  7. EstimateItem   — Ajánlati tételek (pillanatkép)
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class WorkCategory(models.Model):
    """Munkakategória — pl. Kapcsolók és dugaljak, Világítás, Elosztószekrény..."""
    name = models.CharField("Név", max_length=100, unique=True)
    description = models.TextField("Leírás", blank=True)
    order = models.PositiveSmallIntegerField("Sorrend", default=0)

    class Meta:
        verbose_name = "Munkakategória"
        verbose_name_plural = "Munkakategóriák"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class WorkItem(models.Model):
    """Konkrét munkafolyamat normaidővel."""
    UNIT_CHOICES = [
        ('db', 'darab'),
        ('m', 'méter'),
        ('m2', 'négyzetméter'),
        ('km', 'kilométer'),
        ('óra', 'óra'),
        ('alkalom', 'alkalom'),
        ('helyiség', 'helyiség'),
        ('készülék', 'készülék'),
        ('kör', 'áramkör'),
        ('pont', 'pont'),
        ('projekt', 'projekt'),
        ('szerelvény', 'szerelvény'),
        ('csomag', 'csomag'),
    ]

    category = models.ForeignKey(
        WorkCategory,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Kategória"
    )
    name = models.CharField("Munkafolyamat neve", max_length=200)
    unit = models.CharField("Egység", max_length=20, choices=UNIT_CHOICES, default='db')
    base_time_hours = models.DecimalField(
        "Normaidő (óra/db)",
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Egy egységre jutó munkaidő órában. Pl. 0,45 = 27 perc"
    )
    description = models.TextField("Leírás", blank=True)
    is_active = models.BooleanField("Aktív", default=True)
    order = models.PositiveSmallIntegerField("Sorrend", default=0)

    class Meta:
        verbose_name = "Munkafolyamat"
        verbose_name_plural = "Munkafolyamatok"
        ordering = ['category__order', 'order', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_unit_display()})"

    def time_in_minutes(self):
        """Normaidő percben."""
        return float(self.base_time_hours) * 60


class HourlyRate(models.Model):
    """Rezsióradíj — verziózva, a régieket nem töröljük!"""
    name = models.CharField("Megnevezés", max_length=100)
    hourly_rate = models.PositiveIntegerField(
        "Rezsióradíj (Ft/óra)",
        validators=[MinValueValidator(1)],
        help_text="Egy munkaórára eső díj forintban."
    )
    valid_from = models.DateField("Érvényesség kezdete")
    valid_to = models.DateField("Érvényesség vége", null=True, blank=True)
    is_active = models.BooleanField("Aktív", default=True)

    class Meta:
        verbose_name = "Rezsióradíj"
        verbose_name_plural = "Rezsióradíjak"
        ordering = ['-valid_from']

    def __str__(self):
        return f"{self.name} — {self.hourly_rate:,} Ft/óra".replace(',', ' ')


class Multiplier(models.Model):
    """Szorzó — nehézség, sürgősség, régi épület stb."""
    TYPE_CHOICES = [
        ('difficulty', 'Nehézségi szorzó'),
        ('urgency', 'Sürgősségi szorzó'),
        ('building', 'Épület típus szorzó'),
        ('other', 'Egyéb szorzó'),
    ]

    name = models.CharField("Szorzó neve", max_length=100, unique=True)
    type = models.CharField("Típus", max_length=20, choices=TYPE_CHOICES, default='other')
    value = models.DecimalField(
        "Szorzó érték",
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Pl. 1,25 = +25%, 0,90 = -10%"
    )
    is_active = models.BooleanField("Aktív", default=True)
    order = models.PositiveSmallIntegerField("Sorrend", default=0)

    class Meta:
        verbose_name = "Szorzó"
        verbose_name_plural = "Szorzók"
        ordering = ['type', 'order', 'name']

    def __str__(self):
        return f"{self.name} ({self.value})"


class Customer(models.Model):
    """Ügyfél adatok."""
    name = models.CharField("Név", max_length=200)
    address = models.CharField("Cím", max_length=300, blank=True)
    city = models.CharField("Település", max_length=100, blank=True)
    zip_code = models.CharField("Irányítószám", max_length=10, blank=True)
    phone = models.CharField("Telefonszám", max_length=50, blank=True)
    email = models.EmailField("E-mail cím", blank=True)
    note = models.TextField("Megjegyzés", blank=True)
    created_at = models.DateTimeField("Létrehozva", auto_now_add=True)

    class Meta:
        verbose_name = "Ügyfél"
        verbose_name_plural = "Ügyfelek"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.city}" if self.city else self.name


class Estimate(models.Model):
    """Ajánlat — a kalkuláció végeredménye."""
    STATUS_CHOICES = [
        ('draft', 'Piszkozat'),
        ('sent', 'Elküldve'),
        ('accepted', 'Elfogadva'),
        ('rejected', 'Elutasítva'),
        ('closed', 'Lezárva'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='estimates',
        verbose_name="Ügyfél"
    )
    customer_name_override = models.CharField(
        "Ügyfél neve (ha nincs regisztrálva)",
        max_length=200,
        blank=True,
        help_text="Akkor használd, ha az ügyfél nincs az adatbázisban."
    )
    hourly_rate = models.ForeignKey(
        HourlyRate,
        on_delete=models.PROTECT,
        verbose_name="Rezsióradíj",
        help_text="A rezsióradíj nem törölhető, ha ajánlat hivatkozik rá!"
    )
    travel_fee = models.PositiveIntegerField("Kiszállási díj (Ft)", default=0)
    material_cost = models.PositiveIntegerField("Anyagköltség (Ft)", default=0)
    discount_percent = models.DecimalField(
        "Kedvezmény (%)",
        max_digits=4,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    vat_rate = models.DecimalField(
        "ÁFA kulcs (%)",
        max_digits=4,
        decimal_places=1,
        default=27,
        help_text="Alapértelmezetten 27%"
    )
    subtotal_labor = models.PositiveIntegerField("Munkadíj (nettó)", default=0)
    subtotal_material = models.PositiveIntegerField("Anyagköltség (nettó)", default=0)
    total = models.PositiveIntegerField("Végösszeg (bruttó)", default=0)
    note = models.TextField("Megjegyzés", blank=True)
    status = models.CharField(
        "Státusz",
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    created_at = models.DateTimeField("Létrehozva", auto_now_add=True)
    updated_at = models.DateTimeField("Módosítva", auto_now=True)

    class Meta:
        verbose_name = "Ajánlat"
        verbose_name_plural = "Ajánlatok"
        ordering = ['-created_at']

    def __str__(self):
        customer_name = self.customer.name if self.customer else self.customer_name_override
        return f"Ajánlat #{self.id} — {customer_name or 'Névtelen'} ({self.get_status_display()})"

    def customer_display(self):
        if self.customer:
            return str(self.customer)
        return self.customer_name_override or "—"

    def total_labor_hours(self):
        """Összes munkaóra az ajánlatban (szorzókkal korrigálva)."""
        return sum(
            float(item.calculated_hours)
            for item in self.items.all()
        )

    def save(self, *args, **kwargs):
        # A végösszeg újraszámolva (biztonság kedvéért)
        if self.subtotal_labor and self.material_cost is not None:
            subtotal = self.subtotal_labor + self.material_cost + self.travel_fee
            discount = subtotal * self.discount_percent / 100
            after_discount = subtotal - discount
            self.total = int(after_discount * (1 + self.vat_rate / 100))
        super().save(*args, **kwargs)


class EstimateItem(models.Model):
    """Ajánlati tétel — a munkafolyamatok pillanatképe az ajánlat készítésekor."""
    estimate = models.ForeignKey(
        Estimate,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Ajánlat"
    )
    work_item = models.ForeignKey(
        WorkItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Munkafolyamat"
    )
    name = models.CharField("Tétel neve", max_length=200)
    unit = models.CharField("Egység", max_length=20)
    quantity = models.PositiveIntegerField("Mennyiség", default=1)
    base_time_hours = models.DecimalField(
        "Alap normaidő (óra/egység)",
        max_digits=6,
        decimal_places=3
    )
    multiplier_total = models.DecimalField(
        "Összesített szorzó",
        max_digits=6,
        decimal_places=3,
        default=1.0,
        help_text="Az összes kiválasztott szorzó szorzata"
    )
    calculated_hours = models.DecimalField(
        "Számított munkaóra",
        max_digits=8,
        decimal_places=3,
        help_text="mennyiség × alap normaidő × összesített szorzó"
    )
    calculated_price = models.PositiveIntegerField(
        "Számított munkadíj (Ft)",
        help_text="számított munkaóra × rezsióradíj"
    )
    order = models.PositiveSmallIntegerField("Sorrend", default=0)

    class Meta:
        verbose_name = "Ajánlati tétel"
        verbose_name_plural = "Ajánlati tételek"
        ordering = ['order']

    def __str__(self):
        return f"{self.name} — {self.quantity} {self.unit} × {self.calculated_price:,} Ft".replace(',', ' ')
