# Munkadíj Kalkulátor

Villanyszerelési normaidő- és díjkalkulátor — webes + Android (PWA).

## Mit tud?

- **73 előre definiált munkafolyamat** 10 kategóriában (kapcsolók, világítás, elosztószekrény, hibakeresés, kábelezés, vésés, okosotthon, mérőhely, karbantartás...)
- **Normaidő-alapú számítás**: mennyiség × normaidő × szorzók × rezsióradíj = munkadíj
- **13 szorzó**: épület típusa, nehézség, sürgősség, bontás, munkavédelem
- **Extra költségek**: kiszállási díj, anyagköltség, kedvezmény, ÁFA
- **Azonnali eredmény** AJAX-szal, oldal újratöltés nélkül
- **Ajánlat mentése** az adatbázisba
- **PWA támogatás**: Androidon "Telepítés" gomb → app ikon a főképernyőn
- **Django Admin felület**: minden adat (munkafolyamatok, szorzók, rezsióradíjak) kényelmesen szerkeszthető

## Tech stack

- Django 5.2 + SQLite
- Bootstrap 5 (reszponzív, mobilbarát)
- Inter font, bizalomkék-narancs design
- PWA (Service Worker + manifest)
- AJAX (fetch API, oldal újratöltés nélkül)

## Indítás

```bash
cd /home/richard/Asztal/Munkadíj_kalkulátor
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8001
```

Nyisd meg: **http://localhost:8001**

## Admin felület

- **URL:** http://localhost:8001/admin/
- **Felhasználónév:** admin
- **Jelszó:** Admin1234

Az admin felületen tudod:
- Munkafolyamatokat hozzáadni, módosítani, törölni
- Kategóriákat kezelni
- Rezsióradíjakat frissíteni (verziózva, a régi megmarad)
- Szorzók értékét állítani
- Ügyfeleket és ajánlatokat kezelni

## Használat

1. Nyisd meg a **Kezdőlapot**, majd kattints az **"Új kalkuláció indítása"** gombra
2. Válaszd ki a munkafolyamatokat (pipáld be, és állítsd be a mennyiséget)
3. Állítsd be a szorzókat (épület típus, nehézség, sürgősség)
4. Add meg az extra költségeket (kiszállás, anyag, kedvezmény)
5. Kattints a **"Számítás"** gombra — az eredmény azonnal megjelenik
6. Opcionálisan mentsd el az ajánlatot az **"Ajánlat mentése"** gombbal

## Adatok újratöltése

Ha bármikor nulláról szeretnéd kezdeni az adatbázist:

```bash
rm -f db.sqlite3
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
```

## Android telepítés (PWA)

1. Nyisd meg a weboldalt Chrome böngészőben a telefonodon
2. A Chrome menü (⋮) → **"Alkalmazás telepítése"** vagy **"Hozzáadás a főképernyőhöz"**
3. Az app ikon megjelenik a főképernyőn, és ugyanúgy használható mint egy natív alkalmazás

## Fájlstruktúra

```
Munkadíj_kalkulátor/
├── config/             # Django projekt beállítások
│   ├── settings.py
│   └── urls.py
├── kalkulator/         # Fő app
│   ├── models.py       # 7 adatbázis tábla
│   ├── admin.py        # Django Admin regisztráció
│   ├── views.py        # Kalkulátor logika + AJAX endpointok
│   ├── urls.py
│   └── management/commands/
│       └── seed_data.py  # Kezdő adatok betöltése
├── templates/
│   ├── base.html       # Alap template (navbar, footer, PWA)
│   └── kalkulator/
│       ├── home.html   # Kezdőlap
│       └── calculator.html  # Kalkulátor oldal
├── static/
│   ├── css/style.css   # Design rendszer
│   ├── js/sw.js        # Service Worker (PWA)
│   └── manifest.json   # PWA manifest
├── db.sqlite3          # Adatbázis
└── manage.py
```
