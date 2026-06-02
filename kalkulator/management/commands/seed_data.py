"""
Kezdő adatok betöltése — idempotens, többször futtatható.

Futtatás: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from kalkulator.models import WorkCategory, WorkItem, HourlyRate, Multiplier
from datetime import date


# ============================================================
# Kategóriák és munkafolyamatok
# ============================================================
CATEGORIES_DATA = {
    "Alapszerelés": {
        "order": 1,
        "description": "Általános villanyszerelési alapmunkák",
        "items": [
            ("Kapcsoló szerelése (1 kötés)", "db", 0.35),
            ("Kapcsoló szerelése (váltókapcsoló)", "db", 0.50),
            ("Kapcsoló szerelése (keresztváltó)", "db", 0.60),
            ("Szerelvénydoboz felszerelése", "db", 0.30),
            ("Szerelvénykeret rögzítése", "db", 0.20),
            ("Takarókeret felhelyezése", "db", 0.10),
        ]
    },
    "Kapcsolók és dugaljak": {
        "order": 2,
        "description": "Konktorok, dugaljak, kapcsolók szerelése, cseréje",
        "items": [
            ("Konnektor szerelése (süllyesztett)", "db", 0.45),
            ("Konnektor szerelése (falon kívüli)", "db", 0.30),
            ("Konnektor csere", "db", 0.25),
            ("Dugalj szerelése (IP44 védett)", "db", 0.55),
            ("USB-s konnektor szerelése", "db", 0.60),
            ("Padlódoboz szerelése", "db", 0.75),
            ("TV+SAT kombinált csatlakozó szerelése", "db", 0.50),
            ("Internet/RJ45 csatlakozó szerelése", "db", 0.40),
            ("Egyedi csatlakozóaljzat (3 fázis)", "db", 0.70),
        ]
    },
    "Világítás": {
        "order": 3,
        "description": "Lámpatestek, fényforrások szerelése, bekötése",
        "items": [
            ("Mennyezeti lámpa felszerelése", "db", 0.50),
            ("Fali lámpa felszerelése", "db", 0.40),
            ("Sínrendszeres lámpa szerelése", "db", 0.75),
            ("Süllyesztett spotlámpa szerelése", "db", 0.60),
            ("LED szalag szerelése", "m", 0.25),
            ("Mozgásérzékelős lámpa szerelése", "db", 0.65),
            ("Kültéri lámpatest szerelése", "db", 0.70),
            ("Csillár felszerelése", "db", 0.90),
            ("Fényerőszabályozó (dimmer) szerelése", "db", 0.45),
        ]
    },
    "Elosztószekrény": {
        "order": 4,
        "description": "Elosztószekrények, kismegszakítók, FI relék szerelése",
        "items": [
            ("Kismegszakító csere", "db", 0.25),
            ("Kismegszakító új bekötése", "db", 0.40),
            ("FI relé szerelése", "db", 0.45),
            ("Túlfeszültség-védő szerelése", "db", 0.40),
            ("Elosztószekrény bővítése", "alkalom", 2.00),
            ("Új elosztószekrény telepítése (12 modul)", "db", 4.00),
            ("Új elosztószekrény telepítése (24 modul)", "db", 6.00),
            ("Időzítő kapcsolóóra szerelése", "db", 0.60),
            ("Mágneskapcsoló (kontaktor) bekötése", "db", 0.75),
        ]
    },
    "Hibakeresés": {
        "order": 5,
        "description": "Villamos hibák felderítése, diagnosztika",
        "items": [
            ("Áramkör hibakeresése (alap)", "alkalom", 1.50),
            ("Áramkör hibakeresése (komplex)", "alkalom", 3.00),
            ("FI relé leoldás okának keresése", "alkalom", 1.50),
            ("Feszültségmérés és diagnosztika", "alkalom", 1.00),
            ("Zárlatkeresés", "alkalom", 2.00),
            ("Szakadás keresése falon belül", "alkalom", 2.50),
            ("Hőtérképes állapotfelmérés", "alkalom", 1.50),
        ]
    },
    "Kábelezés": {
        "order": 6,
        "description": "Vezetékek, kábelek behúzása, szerelése",
        "items": [
            ("Vezeték behúzása (védőcsőbe)", "m", 0.15),
            ("Kábel fektetése (kábelcsatornában)", "m", 0.12),
            ("Védőcső szerelése (falon kívül)", "m", 0.20),
            ("Kábelösszekötő szerelése", "db", 0.20),
            ("Fővezeték csere (méretlen)", "m", 0.35),
            ("Bekötés mérőórába", "db", 0.50),
            ("Gerincvezeték fektetés", "m", 0.25),
        ]
    },
    "Vésés és bontás": {
        "order": 7,
        "description": "Falvésés, horonymarás, bontási munkák",
        "items": [
            ("Horonymarás (tégla fal)", "m", 0.30),
            ("Horonymarás (beton fal)", "m", 0.60),
            ("Szerelvénydoboz fészek kivésése (tégla)", "db", 0.45),
            ("Szerelvénydoboz fészek kivésése (beton)", "db", 0.80),
            ("Glettelés, vakolás (horony)", "m", 0.20),
            ("Bontás (régi szerelvény)", "db", 0.25),
            ("Áttörés falon (kábel átvezetés)", "db", 0.60),
        ]
    },
    "Okosotthon": {
        "order": 8,
        "description": "Okosotthon rendszerek telepítése, programozása",
        "items": [
            ("Okos relé (Sonoff/Shelly) szerelése", "db", 0.60),
            ("Okoskapcsoló telepítése", "db", 0.50),
            ("Okos redőnyvezérlő szerelése", "db", 0.65),
            ("Okos termosztát telepítése", "db", 0.75),
            ("Okos füstjelző telepítése", "db", 0.40),
            ("Okos ajtó-/ablakérzékelő", "db", 0.30),
            ("Okosotthon központ telepítése", "db", 1.50),
            ("Jelenetek/rutinok programozása", "óra", 1.00),
        ]
    },
    "Mérőhely": {
        "order": 9,
        "description": "Mérőhely kialakítása, szabványosítás",
        "items": [
            ("Mérőhely szabványosítás", "alkalom", 4.00),
            ("Új mérőhely kialakítás", "alkalom", 6.00),
            ("Földelő szonda telepítése", "db", 2.00),
            ("EPH (Egyenpotenciálú hálózat) kialakítása", "alkalom", 3.00),
            ("Mérőhely áthelyezés", "alkalom", 5.00),
        ]
    },
    "Karbantartás": {
        "order": 10,
        "description": "Rendszeres karbantartás, felülvizsgálat",
        "items": [
            ("Éves érintésvédelmi felülvizsgálat", "alkalom", 2.00),
            ("Elosztószekrény karbantartás", "alkalom", 1.50),
            ("Lámpatest tisztítás, ellenőrzés", "db", 0.30),
            ("Villámvédelmi felülvizsgálat", "alkalom", 3.00),
            ("Tűzjelző rendszer karbantartása", "alkalom", 2.00),
            ("Biztonsági világítás ellenőrzése", "alkalom", 1.00),
        ]
    },
}

# ============================================================
# Szorzók
# ============================================================
MULTIPLIERS_DATA = [
    ("Új építés", "building", 0.85, 1),
    ("Panel lakás", "building", 0.90, 2),
    ("Régi épület (1990 előtt)", "building", 1.25, 3),
    ("Műemlék épület", "building", 1.40, 4),
    ("Könnyen hozzáférhető hely", "difficulty", 0.90, 1),
    ("Normál hozzáférhetőség", "difficulty", 1.00, 2),
    ("Nehezen hozzáférhető hely", "difficulty", 1.30, 3),
    ("Magaslati munka (létra/állvány)", "difficulty", 1.40, 4),
    ("Normál munkavégzés", "urgency", 1.00, 1),
    ("Sürgős munka (48 órán belül)", "urgency", 1.30, 2),
    ("Azonnali kiszállás", "urgency", 1.50, 3),
    ("Bontással járó munka", "other", 1.40, 1),
    ("Munkavédelmi többlet", "other", 1.15, 2),
]

# ============================================================
# Rezsióradíj
# ============================================================
HOURLY_RATE_DATA = [
    ("Alap rezsióradíj 2024", 14000, date(2024, 1, 1), None),
]


class Command(BaseCommand):
    help = "Kezdő adatok betöltése: kategóriák, munkafolyamatok, szorzók, rezsióradíj"

    def handle(self, *args, **options):
        self.stdout.write("Kezdő adatok betöltése...\n")

        # --- Kategóriák és munkafolyamatok ---
        for cat_name, cat_data in CATEGORIES_DATA.items():
            category, created = WorkCategory.objects.get_or_create(
                name=cat_name,
                defaults={
                    'description': cat_data['description'],
                    'order': cat_data['order'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Kategória: {cat_name}"))
            else:
                self.stdout.write(f"  • Kategória (már létezik): {cat_name}")

            for idx, (item_name, unit, hours) in enumerate(cat_data['items']):
                item, created = WorkItem.objects.get_or_create(
                    name=item_name,
                    category=category,
                    defaults={
                        'unit': unit,
                        'base_time_hours': hours,
                        'order': idx + 1,
                    }
                )
                if created:
                    perc = hours * 60
                    self.stdout.write(f"     + {item_name} ({hours} ó = {perc:.0f} p)")

        # --- Szorzók ---
        self.stdout.write("")
        for name, mtype, value, order in MULTIPLIERS_DATA:
            obj, created = Multiplier.objects.get_or_create(
                name=name,
                defaults={'type': mtype, 'value': value, 'order': order}
            )
            if created:
                pct = (value - 1) * 100
                sign = '+' if pct >= 0 else ''
                self.stdout.write(self.style.SUCCESS(f"  ✓ Szorzó: {name} ({sign}{pct:.0f}%)"))

        # --- Rezsióradíj ---
        self.stdout.write("")
        for name, rate, valid_from, valid_to in HOURLY_RATE_DATA:
            obj, created = HourlyRate.objects.get_or_create(
                name=name,
                defaults={
                    'hourly_rate': rate,
                    'valid_from': valid_from,
                    'valid_to': valid_to,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Rezsióradíj: {name} — {rate:,} Ft/óra".replace(',', ' ')))

        # --- Statisztika ---
        self.stdout.write("")
        self.stdout.write(f"Összes kategória: {WorkCategory.objects.count()}")
        self.stdout.write(f"Összes munkafolyamat: {WorkItem.objects.count()}")
        self.stdout.write(f"Összes szorzó: {Multiplier.objects.count()}")
        self.stdout.write(f"Összes rezsióradíj: {HourlyRate.objects.count()}")
        self.stdout.write(self.style.SUCCESS("\nKész! Az adatok betöltve."))
