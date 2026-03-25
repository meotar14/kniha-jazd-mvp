# Používateľská Príručka

Tento dokument je stručný návod pre bežného používateľa aplikácie `kniha-jazd-mvp`.

## 1. Prvé Nastavenie

Po prvom spustení otvor záložku `Nastavenia` a vyplň:
- názov spoločnosti
- IČO
- adresu sídla alebo základne
- logo firmy

Tieto údaje sa používajú v hlavičke aplikácie a pri exportoch.

## 2. Založenie Základných Dát

Pred generovaním jázd je potrebné vytvoriť:
- auto
- vodiča
- zákazníkov

### Auto
Vyplň:
- ŠPZ
- model
- priemernú spotrebu
- objem nádrže

### Vodič
Vyplň:
- meno
- číslo vodičského preukazu

### Zákazníci
Pri zákazníkovi vyplň:
- názov
- adresu
- vzdialenosť od základne

Ak vzdialenosť nevieš, môžeš použiť tlačidlo na dopočítanie z mapy.

## 3. Mesačný Plán

V záložke `Plány` vytvor mesačný plán:
- vozidlo
- vodič
- rok a mesiac
- základná adresa
- počiatočný a koncový stav km

Voliteľne môžeš zapnúť:
- `Zohľadniť 10 % súkromných km mimo evidencie jázd`

Tento režim znamená:
- 10 % z mesačného nájazdu sa nebude evidovať v zozname jázd
- tieto km však budú započítané do celkového mesačného plánu

## 4. Tankovania

V záložke `Jazdy` môžeš zapisovať tankovania:
- vyber auto
- zadaj dátum
- litre
- cenu
- mesto
- prípadne označ zahraničie

Mesačný plán sa priradí automaticky podľa auta a dátumu.

## 5. Ručné Jazdy

Ručná jazda slúži na:
- reálne jazdy, ktoré chceš mať explicitne v evidencii
- služobné cesty na viac dní

Pri jazde môžeš zadať:
- mesačný plán
- zákazníka
- dátum
- dátum do
- štart
- cieľ
- vzdialenosť
- poznámku

Ak zadáš rozsah `dátum do`, generátor v týchto dňoch nebude vytvárať ďalšie jazdy.

## 6. Generovanie Jázd

V záložke `Report`:
1. vyber mesačný plán
2. podľa potreby zaškrtni 10 % súkromných km mimo evidencie
3. klikni `Generuj jazdy`

Generátor:
- preferuje pracovné dni
- rešpektuje ručne zadané jazdy
- rešpektuje dátumy tankovania
- negeneruje nezmyselné trasy
- snaží sa držať dĺžku jazdy blízko reálnej vzdialenosti

## 7. Report

Tlačidlo `Načítaj report` zobrazí:
- celkový cieľ km v pláne
- cieľ služobných km
- evidované služobné km
- skryté súkromné km
- spolu započítané km
- natankované litre
- odhadovanú spotrebu
- priemernú spotrebu

## 8. Exporty

### Export Jázd Pre Plán CSV
- jednoduchý export jázd pre vybraný plán

### Export Jázd Pre Plán Excel
- export do excel šablóny knihy jázd
- vypĺňa mesačné záložky za celý rok pre dané auto

### Export Mesačného Plánu: Jazdy + Tankovania
- ročný excel export jázd
- navyše obsahuje hárok `Tankovania`

### Export Reportu CSV
- kontrolný export čísel reportu

### Export Filtrovaných Jázd
- exportuje len to, čo je práve vyfiltrované v tabuľke

## 9. Editácia Záznamov

Každý záznam je možné upraviť tlačidlom `Upraviť`.

Editácia sa otvára ako plný formulár, kde vidíš všetky polia naraz. To platí pre:
- autá
- vodičov
- zákazníkov
- plány
- jazdy
- tankovania

## 10. Záloha A Obnova

V záložke `Nastavenia` je sekcia:
- export zálohy do JSON
- import zálohy z JSON

Odporúčaný postup:
1. pred aktualizáciou spraviť export zálohy
2. odložiť súbor mimo servera
3. až potom robiť update alebo redeploy

## 11. Release A Kontakty

V aplikácii sa zobrazuje:
- release verzia
- kontakt `meotar@airo.sk`
- kontakt `meotar@gmail.com`

Tieto informácie sú viditeľné:
- v hlavičke
- v nastaveniach
- v pravom dolnom rohu aplikácie
