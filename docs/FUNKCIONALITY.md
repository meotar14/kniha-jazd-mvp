# Funkcionality Aplikácie

Tento dokument popisuje hlavné moduly aplikácie `kniha-jazd-mvp`, rozdiely medzi exportmi a väzby medzi tankovaním, generovaním jázd a reportmi.

## Základné Moduly

### Autá
- evidencia vozidiel, ŠPZ, modelu, priemernej spotreby a objemu nádrže
- možnosť nastaviť hlavného vodiča auta
- podklad pre mesačné plány, jazdy, tankovania a reporty

### Vodiči
- evidencia vodičov a ich identifikačných údajov
- vodič sa viaže na mesačný plán a export knihy jázd

### Zákazníci
- evidencia zákazníkov, adries a vzdialenosti od základne
- možnosť povoliť alebo zakázať zákazníka pre automatické generovanie
- podpora globálneho číselníka aj samostatného číselníka pre konkrétne auto
- podpora importu z CSV

### Mesačné Plány
- mesačný plán pre konkrétne auto a vodiča
- obsahuje mesiac, rok, základnú adresu a stav km na začiatku a konci obdobia
- ak ešte nie je známy koncový stav km, plán sa dá uložiť aj priebežne; koncový stav sa dočasne nastaví na počiatočný a neskôr sa upraví
- tvorí hlavnú jednotku pre jazdy, tankovania, reporty a exporty
- pri výbere auta sa vie automaticky predvyplniť jeho hlavný vodič
- pri novom pláne sa vie predvyplniť počiatočný stav km z predchádzajúceho mesiaca rovnakého auta
- základná adresa sa vie zdediť z predchádzajúceho plánu rovnakého auta a vodiča
- ak je `start_odometer_km` prázdne, backend ho vie dopočítať server-side z predchádzajúceho plánu

### Jazdy
- ručne zadané alebo automaticky generované jazdy
- môžu byť jednodňové alebo viacdňové
- viažu sa k mesačnému plánu

### Tankovania
- evidencia tankovaní s dátumom, litrami, cenou, mestom, príznakom zahraničia a voliteľným stavom tachometra
- podľa dátumu sa automaticky priraďujú k správnemu mesačnému plánu

### Report
- kontrolný prehľad mesačného plánu
- zobrazuje cieľové km, skutočné km, natankované litre, odhadovanú a priemernú spotrebu

### Nastavenia
- firma, IČO, logo, adresa základne
- import zákazníkov
- export a import záloh
- evidencia sviatkov a dní pracovného voľna

## Hlavné Funkcionality

- CRUD pre autá, vodičov, zákazníkov, mesačné plány, jazdy a tankovania
- tabuľkové zobrazenia s editáciou a mazaním
- hromadný výber a hromadné mazanie
- `Shift + klik` výber rozsahu riadkov
- filtrovanie plánov podľa auta, vodiča, mesiaca a roka
- filtrovanie jázd podľa plánu, auta, vodiča, mesiaca, roka a typu záznamu
- triedenie zákazníkov podľa mena, vzdialenosti, vytvorenia a poslednej úpravy
- hromadné povoľovanie alebo zakazovanie zákazníkov pre generovanie
- konfigurovateľné stĺpce v zozname jázd
- viditeľné potvrdenie uloženia po vytvorení záznamu
- ručné jazdy s rozsahom dátumov
- import zákazníkov z CSV s mapovaním stĺpcov a dôvodmi chýb
- odhad vzdialenosti zákazníka podľa adresy základne a adresy zákazníka
- upload loga firmy zo súboru
- export a import kompletnej zálohy aplikácie vo formáte JSON
- editácia všetkých entít cez plný formulár v modálnom okne, nie po jednotlivých promptoch
- zobrazenie release verzie a kontaktných e-mailov priamo v UI

## Generovanie Jázd

Generovanie jazd funguje nad mesačným plánom a jeho cieľovým nájazdom.

### Vstupy Pre Generovanie
- počiatočný a koncový stav km v mesačnom pláne
- voliteľné zohľadnenie 10 % súkromných km mimo evidencie jázd
- dostupní zákazníci a ich vzdialenosť od základne
- prípadne vlastný číselník zákazníkov podľa auta
- ručne zadané jazdy
- viacdňové ručné jazdy
- tankovania
- pracovné dni v mesiaci
- sviatky a zadané dni pracovného voľna

### Pravidlá Generovania
- generátor sa snaží dorovnať cieľové km plánu
- preferuje pracovné dni pred víkendmi
- vyhýba sa sviatkom a zadaným dňom pracovného voľna
- rešpektuje dni blokované ručnými jazdami
- negeneruje jazdu `základňa -> základňa`
- nepoužíva zákazníkov, ktorí sú zakázaní pre generovanie
- dĺžka jazdy sa drží približne do 20 % od reálnej trasy tam a späť

### Cieľ Generovania
- vytvoriť realistické jazdy tak, aby sedel mesačný nájazd
- rozložiť jazdy čo najrovnomernejšie počas mesiaca, ak to situácia dovolí

### Súkromné Km Mimo Evidencie
- pri generovaní je možné zapnúť režim, v ktorom sa 10 % celkového mesačného plánu berie ako súkromné km
- tieto km sa generujú ako samostatné jazdy typu `Sukromna jazda`
- nemajú povinný štart ani cieľ
- zobrazujú sa v zozname jázd aj v exportoch
- do plánu sa započítajú pri kontrole celkového mesačného nájazdu
- report preto zobrazuje osobitne:
  evidované služobné km,
  súkromné km,
  celkové km do plánu

## Tankovanie A Súvislosti

Tankovanie nie je len samostatná evidencia, ale aj vstup do logiky generovania a reportovania.

### Väzba Tankovania Na Plán
- používateľ vyberá auto a dátum tankovania
- aplikácia podľa dátumu automaticky vyhľadá správny mesačný plán
- tankovanie sa uloží k plánu bez potreby ručne vyberať plán

### Kontrola Kapacity Nádrže
- auto má evidovaný objem nádrže
- pri kontrole spotreby a logiky tankovaní sa sleduje, aby tankovanie nebolo nereálne voči kapacite vozidla

### Vplyv Na Generovanie Jázd
- generátor zohľadňuje, koľko litrov bolo natankovaných a aká je deklarovaná spotreba auta
- pred dátumom tankovania sa snaží mať dostatočný počet vygenerovaných km, aby tankovanie dávalo zmysel
- tým sa znižuje riziko situácie, že v evidencii je tankovanie, ale jazdy pred ním spotrebu nevysvetľujú

### Vplyv Na Reporty
- report porovnáva natankované litre s očakávanou spotrebou podľa najazdených km
- z reportu je vidno, či tankovania približne zodpovedajú prevádzke auta

## Reporty

Report je určený na kontrolu mesačného plánu.

### Report Obsahuje
- cieľové km podľa plánu
- cieľové služobné km po odpočítaní skrytých súkromných km
- skryté súkromné km
- reálne najazdené km
- počet jázd
- natankované litre
- odhadovanú spotrebu
- priemernú spotrebu za mesiac
- rozdiel medzi očakávaným a reálnym stavom

### Priemerná Spotreba
- počíta sa pre konkrétny mesačný plán
- dostupný je aj prehľad priemernej spotreby podľa auta naprieč plánmi

## Rozdiely Medzi Exportmi

### Export Jázd CSV
- jednoduchý tabuľkový export jázd pre konkrétny plán alebo filter
- vhodný na rýchlu kontrolu alebo ďalšie spracovanie v Exceli

### Export Jázd Excel
- export do excel template knihy jázd
- používa pripravenú šablónu s mesačnými záložkami
- pri exporte za konkrétny plán sa vyplnia všetky dostupné mesiace daného auta a roka
- ak sú zapnuté súkromné km, objavia sa ako samostatné riadky s účelom `Sukromna jazda`

### Export Mesačného Plánu: Jazdy + Tankovania
- používa rovnaký ročný excel template knihy jázd
- okrem mesačných záložiek s jazdami doplní aj samostatný hárok `Tankovania`
- vhodný ako plný kontrolný a archivačný export

### Export Reportu CSV
- číselný kontrolný export reportu
- neslúži ako formálny výstup knihy jázd, ale ako analytický prehľad

### Export Filtrovaných Jázd
- exportuje len to, čo je aktuálne zobrazené podľa filtra
- je vhodný na rýchly výber konkrétneho mesiaca alebo typu záznamu

## Zálohovanie A Obnova

### Export Zálohy
- uloží konfiguráciu a všetky aplikačné dáta do JSON súboru
- vhodné pred aktualizáciou, migráciou alebo zásahom do databázy

### Import Zálohy
- vie obnoviť všetky sekcie naraz alebo len vybrané sekcie
- pri úplnej obnove všetkých sekcií nahradí databázu stavom zo zálohy
- pri čiastočnom importe alebo pri režime bez prepísania bezpečne doplní a aktualizuje vybrané sekcie
- použiteľné pri presune medzi testovacím a ostrým prostredím
- použiteľné aj pri obnove po poškodení alebo zmazaní databázy

## Odporúčaný Pracovný Postup

1. Vytvoriť auto a vodiča.
2. Nastaviť firmu, logo a adresu základne.
3. Importovať alebo vytvoriť zákazníkov a skontrolovať vzdialenosti.
4. Vytvoriť mesačný plán a rozhodnúť, či sa má zohľadňovať 10 % súkromných km mimo evidencie.
5. Zadať reálne tankovania.
6. Zadať ručné jazdy a viacdňové služobné cesty.
7. Spustiť generovanie jázd.
8. Skontrolovať report a spotrebu.
9. Exportovať knihu jázd alebo plný export s tankovaniami.
10. Pred aktualizáciou spraviť JSON zálohu.
