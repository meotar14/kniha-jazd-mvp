# Kniha Jázd MVP (Docker)

Docker-ready backend pre evidenciu jázd a automatické dopočítanie ciest na konci mesiaca.

## 1. Spustenie

```bash
cd kniha-jazd-mvp
cp .env.example .env
mkdir -p /path/to/appdata/kniha-jazd/postgres
docker compose up -d
```

V `.env` nastav hlavne:

```env
POSTGRES_DATA_PATH=/path/to/appdata/kniha-jazd/postgres
APP_PORT=8014
POSTGRES_DB=kniha_jazd
POSTGRES_USER=kniha_user
POSTGRES_PASSWORD=strong_password_here
```

API beží na:

- `http://localhost:8014`
- Swagger docs: `http://localhost:8014/docs`
- Web UI: `http://localhost:8014/ui`

## 2. Čo systém vie

- Evidencia vozidla, vodiča, zákazníkov a ich vzdialenosti od základne
- Možnosť nastaviť na aute hlavného vodiča, ktorý sa pri novom mesačnom pláne predvyplní automaticky
- Evidencia objemu nádrže na vozidle + kontrola, aby tankovanie neprekročilo kapacitu nádrže
- Pri tankovaní je možné vybrať vozidlo a dátum, plán sa priradí automaticky podľa mesiaca
- Evidencia mesačného plánu (`start_odometer_km`, `end_odometer_km`)
- Evidencia tankovaní
- Ručný zápis jázd
- Automatické generovanie chýbajúcich jázd na dorovnanie celkových km (preferencia pracovných dní)
- Mesačný report s porovnaním odhadovanej spotreby a tankovania
- Export jázd a reportu do CSV + export jázd do Excel (.xlsx)
- Export mesačného plánu do jedného Excelu (jazdy + tankovania len z vybraného mesiaca)
- Voliteľné zohľadnenie 10 % súkromných km mimo evidencie jázd
- Editácia a mazanie záznamov priamo z tabuliek (vozidlá, vodiči, zákazníci, plány, jazdy, tankovania)
- Editácia všetkých entít cez plný formulár v modálnom okne
- Výber viacerých riadkov v tabuľkách a hromadné mazanie
- Filter plánov a jázd podľa auta, vodiča, roka a mesiaca
- Export len manuálnych alebo len generovaných jázd
- Záložka Nastavenia: názov firmy, IČO, logo, adresa sídla/základne
- Upload loga aj zo súboru (nielen URL)
- Import zákazníkov z CSV + mapovanie stĺpcov + dôvody zlyhania po riadkoch
- Generátor jázd zohľadňuje dátumy tankovania a preferuje pracovné dni
- Export a import zálohy konfigurácie a všetkých dát (JSON)

## 3. Odporúčaný postup

1. Vytvor vozidlo (`/vehicles`) a vodiča (`/drivers`)
2. Nahraj zoznam zákazníkov (`/customers`)
3. Vytvor mesiac (`/month-plans`)
4. Zapíš reálne tankovania (`/refuels`) a prípadne ručné jazdy (`/trips`)
5. Spusť generovanie (`POST /month-plans/{id}/generate`)
6. Skontroluj report (`GET /month-plans/{id}/report`)
7. Stiahni CSV (`GET /month-plans/{id}/trips.csv`, `GET /month-plans/{id}/report.csv`)

## 4. Rýchly web klient

Po spustení otvor:

- `http://localhost:8014/ui`

V UI vyplníš:

1. vozidlo, vodiča a zákazníkov
2. mesačný plán
3. tankovania a prípadné ručné jazdy
4. tlačidlo na automatické generovanie jázd a export CSV

## 5. Poznámky

- Vzdialenosť ku klientovi je momentálne vstupné číslo (`distance_from_base_km`).
- Ďalší krok: dopojiť online výpočet trás cez Google Maps / OpenRouteService.
- Produkčne používaj reverzný proxy (Traefik/Nginx) a silné heslá v `.env`.
- Verejný Docker image: `ghcr.io/meotar14/kniha-jazd-mvp:latest`

## 6. Dokumentácia

- Detailný prehľad funkcionalít, exportov a väzieb na tankovanie: [`docs/FUNKCIONALITY.md`](docs/FUNKCIONALITY.md)
- Používateľská príručka: [`docs/UZIVATELSKA_PRIRUCKA.md`](docs/UZIVATELSKA_PRIRUCKA.md)
