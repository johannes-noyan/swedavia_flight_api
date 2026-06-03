# Swedavia Flight API - Terminalklient

Denna Python-applikation hjälper dig att bevaka flygdata och göra djupanalyser av tider, statusar och destinationer för Sveriges 10 statliga flygplatser som drivs av Swedavia.

Terminalgränssnittet, alla instruktioner, rullningsmenyer, förklaringar och tabeller är helt på **svenska** för bästa användarvänlighet, medan koden och programmeringskommentarerna är på engelska enligt branschstandard.

---

## Vad gör applikationen?

Applikationen kopplar upp sig mot Swedavias officiella **FlightInfo API v2** och ger dig tillgång till realtidssökningar för:
- 🛬 **Ankommande flyg** (timmar, gater, bagageband, status)
- 🛫 **Avgående flyg** (destinationer, terminaler, status, gater)
- 🔍 **Flightnummersökning** (hitta en specifik flight t.ex. SK532)
- 📊 **Destinationsstatistik** (räknar antal flighter till olika städer och mappar dem mot rätt land med hjälp av en lokal databas)
- 💓 **Hälsokontroll** (veriferar att API-anslutningen är online och fungerar)

---

## Hur startar man applikationen?

1. Säkerställ att du har Python 3 installerat på din dator.
2. Öppna din terminal/kommandotolk.
3. Installera stöd för externa anrop (valfritt):
   ```bash
   pip install requests
   ```
4. Starta programmet:
   ```bash
   python airport.py
   ```

*Om du har en egen API-nyckel från Swedavias utvecklarportal, glöm inte att exportera den som en miljövariabel innan du startar:*
```bash
export SWEDAVIA_API_KEY="din_nyckel_här"
```
*Om ingen nyckel hittas startar programmet automatiskt i ett pedagogiskt **simuleringsläge** med fiktiva men realistiska flighter för att du ska kunna testa alla funktioner direkt!*

---

## Användning & Navigering

När du startar möts du av följande huvudmeny på svenska:

```text
==================================================
Swedavia FlightInfo API v2 - Python-klient
==================================================
1. Ankomster (arrivals) för en flygplats & datum
2. Avgångar (departures) för en flygplats & datum
3. Sök specifikt flightnummer
4. OData-förfrågan (query) eller fritext-filtrering
5. HeartBeat - hälsokontroll av API
6. Demonstrera alla endpoints automatiskt
q. Avsluta
===================================================
```

Skriv in en siffra [1-6] eller `q` och tryck på **Enter**:

### Praktiskt exempel 1: Kolla ankomster på Arlanda idag
1. Välj alternativ `1`.
2. Ange vilken flygplats du vill kolla på. Du kan skriva flygplatsens IATA (t.ex. `arn`) eller flygplatsens namn (t.ex. `arlanda`). Tryck på Enter.
3. Ange datum. Du kan skriva `idag`, `nu`, `imorgon`, `igår` eller ange ett datum rent (t.ex. `2026-06-02`).
4. Flygen visas i block om 50 flighter åt gången.
   - Tryck på **Enter** för att ladda nästa 50 flighter.
   - Skriv `a` och tryck Enter för att ladda och visa alla flighter direkt.
   - Skriv `q` och tryck Enter för att återgå till huvudmenyn.

### Praktiskt exempel 2: Söka specifikt flightnummer
1. Välj alternativ `3`.
2. Ange `SK532` eller `LH819`.
3. Ange datum (t.ex. `idag`).
4. Systemet letar upp flyget över alla Swedavias flygplatser och visar det i ett snyggt, lättläst kort.

---

## Hur fungerar landsmappningen (`city_country.json`)?

Filen `city_country.json` fungerar som en extern, blixtsnabb, lokal databas. Den är framtagen direkt från Swedavias officiella statistik över utrikespassagerare under 2025.

Databasen mappar 263 olika städer till 59 olika länder. Mappningslogiken i koden (`destinationer.py`) är robust byggd för att hantera att flygplatser ibland använder olika stavningar eller tilläggskoder (t.ex. att "London LHR" och "London" båda mappar korrekt till landet "Great Britain").
