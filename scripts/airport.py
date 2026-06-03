# -*- coding: utf-8 -*-
"""
airport.py

Main interactive Swedavia FlightInfo API v2 client.
This file provides a terminal-based Swedish user interface to fetch and analyze flight data
for Sweden's 10 Swedavia airports.

If no SWEDAVIA_API_KEY environment variable is configured, the application runs in a
realistic Simulated Sandbox mode that mimics the Swedavia API payload structures.
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta

# Try to import requests for live API communication. Fallback is handled gracefully.
try:
    import requests
except ImportError:
    requests = None

# Import helper statistics module
try:
    import destinationer
except ImportError:
    destinationer = None


# --- Swedavia Configuration & Constants ---

SWEDAVIA_BASE_URL = "https://api.swedavia.se/flightinfo/v2"

# 10 Swedavia Airports
AIRPORTS = {
    "ARN": "Stockholm Arlanda",
    "GOT": "Göteborg Landvetter",
    "BMA": "Stockholm Bromma",
    "MMX": "Malmö",
    "LLA": "Luleå",
    "UME": "Umeå",
    "OSD": "Östersund",
    "VBY": "Visby",
    "RNB": "Ronneby",
    "KRN": "Kiruna"
}


# --- Time Helpers ---

def get_swedish_date(term):
    """
    Translates Swedish relative terms like 'nu', 'idag', 'imorgon', 'igör' (normalized to igår)
    into standard YYYY-MM-DD strings.
    """
    term_clean = term.strip().lower()
    today_dt = datetime.now()
    
    if term_clean in ('nu', 'idag'):
        return today_dt.strftime('%Y-%m-%d')
    elif term_clean == 'imorgon':
        return (today_dt + timedelta(days=1)).strftime('%Y-%m-%d')
    elif term_clean in ('igår', 'igör'):
        return (today_dt - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Validate if it matches format YYYY-MM-DD
    if re.match(r'^\d{4}-\d{2}-\d{2}$', term_clean):
        return term_clean
    return None

def parse_time_utc_cet(iso_str):
    """
    Converts an ISO 8601 UTC time string like '2026-02-25T17:55:00Z'
    to standard Sweden local time (CET or CEST depending on month).
    """
    if not iso_str:
        return "-"
    try:
        # Standardize formatting
        iso_str = iso_str.replace('Z', '')
        if 'T' in iso_str:
            parts = iso_str.split('T')
            dt_part_str = parts[1].split('.')[0] # e.g., '17:55:00'
            dt_all = datetime.strptime(parts[0] + " " + dt_part_str, "%Y-%m-%d %H:%M:%S")
        else:
            dt_all = datetime.strptime(iso_str.split('.')[0], "%Y-%m-%d %H:%M:%S")
            
        h, m = dt_all.hour, dt_all.minute
        
        # Determine Swedish offset: CEST (UTC+2) is active April to October; else CET (UTC+1).
        # We simplify month lookup: April=4 to October=10
        month = dt_all.month
        offset = 2 if (4 <= month <= 10) else 1
        tz_name = "CEST" if offset == 2 else "CET"
        
        # Apply local offset
        local_hour = (h + offset) % 24
        
        return f"{h:02d}:{m:02d} UTC → {local_hour:02d}:{m:02d} {tz_name}"
    except Exception:
        # Fallback to returning raw string if parse fails
        return iso_str


# --- Airport Code Normalization ---

def normalize_airport_iata(user_input):
    """
    Checks if user inputs a valid IATA, or partial Swedish/English city name,
    and returns its corresponding Swedavia airport IATA code.
    """
    inp = user_input.strip().upper()
    if inp in AIRPORTS:
        return inp
        
    for code, name in AIRPORTS.items():
        if inp in name.upper() or name.upper() in inp:
            return code
            
    # Substring fallback search
    for code, name in AIRPORTS.items():
        # Look at city name (first word)
        city_part = name.split()[0].upper()
        if city_part in inp or inp in city_part:
            return code
            
    return None


# --- Simulated Data Store for Sandbox ---
# Extremely helpful for standalone execution when a subscription key is not available.

def generate_mock_flight(idx, airport, mode, date_str):
    """
    Generates realistic looking flight payloads mirroring Swedavia API schemas.
    """
    is_arr = (mode == "arrivals")
    
    # Mock databases of cities and airlines
    airlines = [
        ("SK532", "SAS Scandinavian Airlines", "SK"),
        ("LH819", "Lufthansa", "LH"),
        ("BA762", "British Airways", "BA"),
        ("DY412", "Norwegian Air Shuttle", "DY"),
        ("AF113", "Air France", "AF"),
        ("AY801", "Finnair", "AY"),
        ("KL110", "KLM Royal Dutch Airlines", "KL"),
        ("FR602", "Ryanair", "FR")
    ]
    
    cities = [
        "London LHR", "Frankfurt", "Paris CDG", "Amsterdam", "Helsinki", 
        "Copenhagen", "Munich", "Alicante", "Split", "Brussels", "New York JFK"
    ]
    
    flight_pick = airlines[idx % len(airlines)]
    city_pick = cities[(idx + 4) % len(cities)]
    
    carrier_code = flight_pick[2]
    flight_no = f"{carrier_code}{100 + idx*7}"
    airline_name = flight_pick[1]
    
    sched_hour = (6 + idx * 2) % 24
    sched_minute = (idx * 15) % 60
    sched_time_str = f"{date_str}T{sched_hour:02d}:{sched_minute:02d}:00Z"
    
    # Baggage, gate, terminal numbers
    terminal = f"T5" if airport == "ARN" else f"T1"
    gate = f"{11 + (idx % 20)}" if (idx % 5 != 0) else "N/A"
    baggage = f"{(idx % 6) + 1}" if is_arr else "N/A"
    
    # D/I Status (Domestic, International, Schengen)
    di = "I" if "New York" in city_pick else ("S" if city_pick != "London LHR" else "I")
    if idx % 7 == 0:
        di = "D" # Domestic
        city_pick = "Visby" if airport == "ARN" else "Stockholm Arlanda"
        
    status = "Landed" if is_arr else "Departed"
    if idx > 8:
        status = "Scheduled"
        
    # Format actual / estimated times
    est_str = ""
    act_str = ""
    remarks = []
    
    if status in ("Landed", "Departed"):
        # Dep/Arr slightly early or late
        diff_minutes = (idx % 7) - 3 # -3 to +3 minutes
        act_hour = (sched_hour + (sched_minute + diff_minutes) // 60) % 24
        act_minute = (sched_minute + diff_minutes) % 60
        act_str = f"{date_str}T{act_hour:02d}:{act_minute:02d}:00Z"
        if diff_minutes > 0:
            remarks = [{"swedish": f"Departed {act_hour:02d}:{act_minute:02d}", "english": f"Departed {act_hour:02d}:{act_minute:02d}"}] if not is_arr else [{"swedish": f"Landat {act_hour:02d}:{act_minute:02d}", "english": f"Landed {act_hour:02d}:{act_minute:02d}"}]
    
    # Assemble standard format
    flight_data = {
        "flightId": f"{flight_no}_{idx}",
        "flightNumber": flight_no,
        "carrierId": carrier_code,
        "carrierName": airline_name,
        "airline": {"name": airline_name},
        "terminal": terminal,
        "gate": gate,
        "baggageBelt": baggage,
        "baggage": baggage,
        "domesticInternational": di,
        "status": status,
        "scheduled": sched_time_str,
        "estimated": est_str,
        "actual": act_str,
        "remarks": remarks
    }
    
    # Source / Destination
    if is_arr:
        flight_data["departureAirport"] = {"english": city_pick, "swedish": city_pick, "iata": "MOCK"}
        flight_data["arrivalAirport"] = {"english": AIRPORTS[airport], "swedish": AIRPORTS[airport], "iata": airport}
    else:
        flight_data["departureAirport"] = {"english": AIRPORTS[airport], "swedish": AIRPORTS[airport], "iata": airport}
        flight_data["arrivalAirport"] = {"english": city_pick, "swedish": city_pick, "iata": "MOCK"}
        
    return flight_data


def get_mock_flights_dataset(airport, mode, date_str):
    """
    Returns a comprehensive set of 60 mock flights for tests.
    """
    flights = []
    for i in range(60):
        flights.append(generate_mock_flight(i, airport, mode, date_str))
    return flights


# --- Parsed Flight Representation Object ---

def parse_swedavia_flight(f, flight_type=None):
    """
    Standardizes raw JSON flight payload objects into elegant unified Python dictionaries.
    """
    inner = f
    is_arr = True
    
    if "arrival" in f:
        inner = f["arrival"]
        is_arr = True
    elif "departure" in f:
        inner = f["departure"]
        is_arr = False
    elif flight_type is not None:
        is_arr = (flight_type == "arrivals" or flight_type == "A")
        
    flight_number = inner.get("flightNumber") or inner.get("flightId") or "N/A"
    carrier_code = inner.get("carrierId") or ""
    
    # Resolve airline name safely
    airline_obj = inner.get("airline") or {}
    if isinstance(airline_obj, dict):
        airline_name = airline_obj.get("name") or inner.get("carrierName") or ""
    else:
        airline_name = str(airline_obj) or inner.get("carrierName") or ""
        
    if not airline_name:
        airline_name = carrier_code or "N/A"
        
    # Departure & Arrival location mapping
    from_airport = "N/A"
    to_airport = "N/A"
    
    dep_obj = inner.get("departureAirport")
    if isinstance(dep_obj, dict):
        from_airport = dep_obj.get("english") or dep_obj.get("swedish") or dep_obj.get("iata") or "N/A"
    else:
        from_airport = inner.get("departureAirportEnglish") or inner.get("departureAirportSwedish") or inner.get("departureAirportIata") or "N/A"
        
    arr_obj = inner.get("arrivalAirport")
    if isinstance(arr_obj, dict):
        to_airport = arr_obj.get("english") or arr_obj.get("swedish") or arr_obj.get("iata") or "N/A"
    else:
        to_airport = inner.get("arrivalAirportEnglish") or inner.get("arrivalAirportSwedish") or inner.get("arrivalAirportIata") or "N/A"
        
    # Capture city parts safely for statistics (removes iatas e.g., "London LHR" -> "London")
    from_city = "N/A"
    if from_airport and from_airport != "N/A":
        from_city = from_airport.split('(')[0].strip()
        
    to_city = "N/A"
    if to_airport and to_airport != "N/A":
        to_city = to_airport.split('(')[0].strip()
        
    status = inner.get("status") or "Scheduled"
    terminal = inner.get("terminal") or "N/A"
    gate = inner.get("gate") or "N/A"
    baggage = inner.get("baggageBelt") or inner.get("baggage") or "N/A"
    di = inner.get("domesticInternational") or "I"
    
    sched = inner.get("scheduled") or inner.get("scheduledDepartureTimeUtc") or inner.get("scheduledArrivalTimeUtc") or ""
    est = inner.get("estimated") or inner.get("estimatedDepartureTimeUtc") or inner.get("estimatedArrivalTimeUtc") or ""
    act = inner.get("actual") or inner.get("actualDepartureTimeUtc") or inner.get("actualArrivalTimeUtc") or ""
    
    remarks_list = inner.get("remarks") or []
    remarks_str = ""
    if isinstance(remarks_list, list):
        texts = []
        for r in remarks_list:
            if isinstance(r, dict):
                text_se = r.get("swedish") or r.get("english") or ""
                if text_se:
                    texts.append(text_se)
            elif isinstance(r, str):
                texts.append(r)
        remarks_str = ", ".join(texts)
    elif isinstance(remarks_list, str):
        remarks_str = remarks_list
        
    return {
        "flight_number": flight_number,
        "airline": airline_name,
        "carrier_code": carrier_code,
        "from_airport": from_airport,
        "to_airport": to_airport,
        "from_city": from_city,
        "to_city": to_city,
        "status": status,
        "terminal": terminal,
        "gate": gate,
        "baggage": baggage,
        "sched_utc": sched,
        "est_utc": est,
        "act_utc": act,
        "di": di,
        "remarks": remarks_str,
        "is_arrival": is_arr
    }


# --- API Request Handler Core Class ---

class SwedaviaClient:
    """
    Handles connections to Swedavia's FlightInfo API, managing authentication,
    sandbox simulation modes, validation, and request pipelines.
    """
    def __init__(self):
        # Look up API key in environment variables: SWEDAVIA_API_KEY
        self.api_key = (
            os.environ.get("SWEDAVIA_API_KEY") or 
            os.environ.get("Ocp-Apim-Subscription-Key") or 
            "0652d4a747e9450c8ba858e5955faeb6"
        )
        self.simulated = not self.api_key
        
    def check_health(self):
        """
        Executes a heartbeat health check. Returns a tuple: (Success Flag, Info Message)
        """
        if self.simulated:
            return True, "HEARTBEAT OK: 200 (Simuleringsläge - Swedavia Sandbox är aktiv)"
            
        if not requests:
            return False, "Biblioteket 'requests' saknas i Python, kan ej nå Swedavias servrar."
            
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Accept": "application/json"
        }
        url = f"{SWEDAVIA_BASE_URL}/heartBeat"
        
        try:
            print(f"+ GET {url}")
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                return True, f"HEARTBEAT OK: 200 (Live Swedavia API svarar)"
            else:
                return False, f"Felkod {r.status_code} returnerades från Swedavia: {r.text}"
        except Exception as e:
            return False, f"Nätverksfel vid hälsokontroll: {str(e)}"
            
    def get_flights(self, airport, mode, date_str):
        """
        Retrieves flight listings forarrivals or departures.
        - airport: normalized airport IATA code (e.g. 'ARN')
        - mode: 'arrivals' or 'departures'
        - date_str: date string (YYYY-MM-DD)
        """
        if self.simulated:
            # Generate local offline dataset
            mock_data = get_mock_flights_dataset(airport, mode, date_str)
            parsed = [parse_swedavia_flight(f, mode) for f in mock_data]
            return True, parsed, "SIMULERING"
            
        if not requests:
            return False, [], "Python 'requests' installationsfel."
            
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Accept": "application/json"
        }
        url = f"{SWEDAVIA_BASE_URL}/{airport}/{mode}/{date_str}"
        
        try:
            print(f"\n+ GET {url}")
            r = requests.get(url, headers=headers, timeout=12)
            if r.status_code == 200:
                payload = r.json()
                # Parse flights array out of Swedavia payload
                flights_raw = []
                if isinstance(payload, list):
                    flights_raw = payload
                elif isinstance(payload, dict):
                    flights_raw = payload.get("flights") or payload.get("arrivals") or payload.get("departures") or []
                
                parsed = [parse_swedavia_flight(f, mode) for f in flights_raw]
                return True, parsed, "LIVE"
            elif r.status_code == 401:
                return False, [], "Auktoriseringsfel (401): Din SWEDAVIA_API_KEY är ogiltig."
            elif r.status_code == 404:
                return False, [], f"Flygplatsen '{airport}' eller datumet '{date_str}' hittades inte (404)."
            else:
                return False, [], f"API-fel (Kod {r.status_code}): {r.text}"
        except Exception as e:
            return False, [], f"Anslutningsfel: {str(e)}"

    def search_by_flight_number(self, flight_number, date_str):
        """
        Uses OData system queries to find a specific flight number.
        """
        # Normalize search string
        fn_clean = flight_number.strip().upper()
        
        if self.simulated:
            # Look up across our ARN and GOT simulation datasets
            found = []
            for apt in ["ARN", "GOT"]:
                for mode in ["arrivals", "departures"]:
                    mock_data = get_mock_flights_dataset(apt, mode, date_str)
                    for f in mock_data:
                        parsed = parse_swedavia_flight(f, mode)
                        if parsed["flight_number"].upper() == fn_clean:
                            found.append(parsed)
            return True, found, "SIMULERING"
            
        if not requests:
            return False, [], "Python 'requests' installationsfel."
            
        # OData structure filter parameters
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Accept": "application/json"
        }
        filter_query = f"flightNumber eq '{fn_clean}' and scheduled eq '{date_str}'"
        url = f"{SWEDAVIA_BASE_URL}/query?$filter={filter_query}"
        
        try:
            print(f"\n+ GET {url}")
            r = requests.get(url, headers=headers, timeout=12)
            if r.status_code == 200:
                payload = r.json()
                raw_flights = []
                if isinstance(payload, list):
                    raw_flights = payload
                elif isinstance(payload, dict):
                    raw_flights = payload.get("flights") or payload.get("value") or []
                    
                parsed = [parse_swedavia_flight(f) for f in raw_flights]
                return True, parsed, "LIVE"
            else:
                return False, [], f"OData Sökfel (Kod {r.status_code}): {r.text}"
        except Exception as e:
            return False, [], f"Sökanslutningsfel: {str(e)}"

    def run_odata_filter(self, filter_expression):
        """
        Sends flat raw OData query strings directly to Swedavia servers.
        """
        if self.simulated:
            # Filter the simulated mock lists
            # Handles queries like "airport eq 'ARN' and scheduled eq '2026-02-26'"
            # Parse airport out of query
            apt_match = re.search(r"airport eq '([A-Z]{3})'", filter_expression, re.IGNORECASE)
            date_match = re.search(r"scheduled eq '(\d{4}-\d{2}-\d{2})'", filter_expression, re.IGNORECASE)
            
            apt = apt_match.group(1).upper() if apt_match else "ARN"
            date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")
            
            # Combine mock files
            mock_arr = get_mock_flights_dataset(apt, "arrivals", date)
            mock_dep = get_mock_flights_dataset(apt, "departures", date)
            
            arr_parsed = [parse_swedavia_flight(f, "arrivals") for f in mock_arr]
            dep_parsed = [parse_swedavia_flight(f, "departures") for f in mock_dep]
            
            return True, arr_parsed + dep_parsed, "SIMULERING"
            
        if not requests:
            return False, [], "Python 'requests' saknas."
            
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Accept": "application/json"
        }
        url = f"{SWEDAVIA_BASE_URL}/query?$filter={filter_expression}"
        
        try:
            print(f"\n+ GET {url}")
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                payload = r.json()
                raw_flights = []
                if isinstance(payload, list):
                    raw_flights = payload
                elif isinstance(payload, dict):
                    raw_flights = payload.get("flights") or payload.get("value") or []
                    
                parsed = [parse_swedavia_flight(f) for f in raw_flights]
                return True, parsed, "LIVE"
            else:
                return False, [], f"OData Query fel {r.status_code}: {r.text}"
        except Exception as e:
            return False, [], f"OData anslutningsfel: {str(e)}"


# --- Terminal Presenter Rendering Engine ---

def render_flight_card(fl, idx, total_count):
    """
    Displays single flight inside high contrast styled ASCII card.
    """
    is_arr = fl["is_arrival"]
    card_header = f"[{idx}] + {fl['flight_number']} | {fl['airline']}"
    
    # Capitalize DI string
    di_raw = fl["di"]
    
    print("-" * 55)
    print(card_header)
    
    if is_arr:
        print(f"From  : {fl['from_airport']}")
        print(f"To    : ({fl['to_airport']})")
    else:
        print(f"From  : ({fl['from_airport']})")
        print(f"To    : {fl['to_airport']}")
        
    print(f"Status: {fl['status']}")
    print(f"Term  : {fl['terminal']:<9} Gate: {fl['gate']}")
    print(f"Bagg  : {fl['baggage']}")
    
    # Times Formatting
    sched_formatted = parse_time_utc_cet(fl["sched_utc"])
    est_formatted = parse_time_utc_cet(fl["est_utc"])
    act_formatted = parse_time_utc_cet(fl["act_utc"])
    
    print(f"Sched : {sched_formatted}")
    print(f"Est   : {est_formatted}")
    print(f"Actual: {act_formatted}")
    print(f"D/I   : {di_raw}")
    if fl["remarks"]:
        print(f"Remarks: {fl['remarks']}")
    print("-" * 55)


def display_flights_paginated(flights, is_arrival=True):
    """
    Shows flights 50 at a time, implementing standard Swedavia pagination.
    """
    total = len(flights)
    if total == 0:
        print("\nInga flygningar hittades för detta sökval.")
        return
        
    idx = 0
    while idx < total:
        chunk = flights[idx:idx+50]
        for f_idx, f_data in enumerate(chunk):
            render_flight_card(f_data, idx + f_idx + 1, total)
            
        remaining = total - (idx + len(chunk))
        shown = idx + len(chunk)
        
        print(f"- Visar {shown}/{total} - ({remaining} kvar)")
        
        if remaining <= 0:
            input("\nAlla flygningar har visats. Tryck på [Enter] för att fortsätta...")
            break
            
        print("\n[Enter] nästa sida | [a] visa alla | [q] tillbaka till menyn: ", end="")
        answer = input().strip().lower()
        
        if answer == 'q':
            break
        elif answer == 'a':
            # Display all remaining flights instantly
            idx += len(chunk)
            while idx < total:
                render_flight_card(flights[idx], idx + 1, total)
                idx += 1
            input("\nAlla flygningar har visats. Tryck på [Enter] för att fortsätta...")
            break
        else:
            idx += 50


# --- Interactive CLI Dialog Handlers ---

def prompt_airport_flow():
    """
    Asks the Swedish user to enter airport and normalizes it.
    """
    print("\nTillgängliga flygplatser:")
    for code, text in AIRPORTS.items():
        print(f"{code} - {text}")
        
    while True:
        choice = input("Ange IATA-kod eller stadsnamn (t.ex. ARN eller Visby): ").strip()
        if not choice:
            print("Inmatningen kan inte vara tom. Försök igen.")
            continue
            
        code = normalize_airport_iata(choice)
        if code:
            return code
        else:
            print(f"Kunde inte hitta flygplatsen '{choice}'. Försök igen.")

def prompt_date_flow():
    """
    Asks the Swedish user to input a date or relative term and validates it.
    """
    while True:
        choice = input("Ange datum (YYYY-MM-DD / nu / idag / imorgon / igår): ").strip()
        if not choice:
            # Default is today
            return get_swedish_date("idag")
            
        resolved_date = get_swedish_date(choice)
        if resolved_date:
            return resolved_date
        else:
            print("Ogiltigt datumformat. Använd YYYY-MM-DD eller ett relativt sökord.")


# --- CLI Routing Menu ---

def main_cli_loop():
    client = SwedaviaClient()
    
    # Print launch header information
    print("=" * 60)
    print("        SWEDAVIA FLIGHTINFO API v2 CLIENT")
    print("=" * 60)
    if client.simulated:
        print("❗ MILJÖVARNING: Ingen SWEDAVIA_API_KEY hittades i systemet.")
        print("👉 Programmet körs i ett interaktivt SIMULERINGSLÄGE.")
        print("👉 För att använda skarpa och äkta realtidsdata, ställ in din")
        print("   SWEDAVIA_API_KEY under 'Secrets' panelen i AI Studio.")
    else:
        print("💚 STATUS: SWEDAVIA_API_KEY är laddad! Ansluter live till API-servern.")
    print("=" * 60 + "\n")
    
    while True:
        print("==================================================")
        print("Swedavia FlightInfo API v2 - Python-klient")
        print("==================================================")
        print("1. Ankomster (arrivals) för en flygplats & datum")
        print("2. Avgångar (departures) för en flygplats & datum")
        print("3. Sök specifikt flightnummer")
        print("4. OData-förfrågan (query) eller fritext-filtrering")
        print("5. HeartBeat - hälsokontroll av API")
        print("6. Demonstrera alla endpoints automatiskt")
        print("q. Avsluta")
        print("===================================================")
        
        choice = input("\nVälj [1-6] eller q: ").strip().lower()
        
        if choice == 'q':
            print("\nTack för att du använde Swedavia FlightInfo API v2. Hejdå!")
            break
            
        elif choice == '1':
            airport = prompt_airport_flow()
            date = prompt_date_flow()
            
            print(f"\nHämtar ankomster för {AIRPORTS[airport]} på datum: {date}...")
            ok, flights, source = client.get_flights(airport, "arrivals", date)
            
            if ok:
                display_flights_paginated(flights, is_arrival=True)
            else:
                print(f"\n❌ FEL: {flights}") # Flights contains error message string here
                input("\nTryck på [Enter] för att fortsätta...")
                
        elif choice == '2':
            airport = prompt_airport_flow()
            date = prompt_date_flow()
            
            # Additional option: upcoming flights only?
            upcoming_only = input("Bara kommande (ej redan avgångna)? (j/n, Enter=alla): ").strip().lower()
            
            print(f"\nHämtar avgångar för {AIRPORTS[airport]} på datum: {date}...")
            ok, flights, source = client.get_flights(airport, "departures", date)
            
            if ok:
                if upcoming_only == 'j':
                    # Parse only upcoming sched flights
                    flights = [f for f in flights if f["status"].lower() == "scheduled"]
                display_flights_paginated(flights, is_arrival=False)
            else:
                print(f"\n❌ FEL: {flights}")
                input("\nTryck på [Enter] för att fortsätta...")
                
        elif choice == '3':
            flight_num = input("\nAnge flightnummer (t.ex. SK532 eller LH819): ").strip()
            date = prompt_date_flow()
            
            if not flight_num:
                print("Flightnummer kan inte vara tomt.")
                continue
                
            print(f"\nSöker efter flyg {flight_num} på datum {date}...")
            ok, flights, source = client.search_by_flight_number(flight_num, date)
            
            if ok:
                if not flights:
                    print(f"Hittade inga flighter med nummer {flight_num} under {date}.")
                else:
                    display_flights_paginated(flights)
            else:
                print(f"\n❌ FEL: {flights}")
                input("\nTryck på [Enter] för att fortsätta...")
                
        elif choice == '4':
            print("\nOData-frågespråk. Ange filteruttryck.")
            print("Exempel på OData filter:")
            print("  airport eq 'ARN' and scheduled eq '2026-02-26'")
            print("  flightNumber eq 'SK532'")
            
            expr = input("\nFilteruttryck: ").strip()
            if not expr:
                print("Filter kan inte vara tomt.")
                continue
                
            print(f"Skickar OData-frågesträng: {expr}...")
            ok, flights, source = client.run_odata_filter(expr)
            
            if ok:
                display_flights_paginated(flights)
            else:
                print(f"\n❌ OData-fel: {flights}")
                input("\nTryck på [Enter] för att fortsätta...")
                
        elif choice == '5':
            print("\nHämtar API-hälsa (heartBeat)...")
            ok, msg = client.check_health()
            if ok:
                print(f"\n💚 HEALTHCHECK SUCCEEDED")
                print(msg)
            else:
                print(f"\n❌ HEALTHCHECK FAILED")
                print(msg)
            input("\nTryck på [Enter] för att fortsätta...")
            
        elif choice == '6':
            print("\n" + "="*50)
            print("  AUTOMATISK DEMO AV SWEDAVIA API ENDPOINTS")
            print("="*50)
            
            print("\n🎬 Steg 1: Kör HeartBeat hälso-kontroll...")
            ok, msg = client.check_health()
            print(f"Resultat: {'OK 💚' if ok else 'FEL ❌'}\n{msg}")
            
            print("\n🎬 Steg 2: Hämtar realtids ankomster för stockholm (ARN)...")
            today_str = get_swedish_date("idag")
            ok, fl_arr, src = client.get_flights("ARN", "arrivals", today_str)
            if ok:
                print(f"Hämtat lyckat! Sektion: {src}. Totalt ankomster hittade: {len(fl_arr)}.")
                if fl_arr:
                    print("Visar första hämtade flygkortet as förhandsgranskning:")
                    render_flight_card(fl_arr[0], 1, len(fl_arr))
            else:
                print(f"Hämtningsfel: {fl_arr}")
                
            print("\n🎬 Steg 3: Hämtar realtids avgångar för Göteborg (GOT)...")
            ok, fl_dep, src = client.get_flights("GOT", "departures", today_str)
            if ok:
                print(f"Hämtat lyckat! Sektion: {src}. Totalt avgångar hittade: {len(fl_dep)}.")
                if fl_dep:
                    print("Visar första avgångskortet:")
                    render_flight_card(fl_dep[0], 1, len(fl_dep))
            else:
                print(f"Hämtningsfel: {fl_dep}")
                
            print("\n🎬 Steg 4: OData-filtrering efter specifika parametrar...")
            demo_expr = f"airport eq 'ARN' and scheduled eq '{today_str}'"
            print(f"Aktiverar sökning: {demo_expr}")
            ok, parsed_odata, src = client.run_odata_filter(demo_expr)
            if ok:
                print(f"Sökning lyckades! Sektion: {src}. Antal träffar: {len(parsed_odata)}")
            else:
                print(f"Sökfel: {parsed_odata}")
                
            print("\n" + "="*50)
            print("              DEMO SLUTFÖRD")
            print("="*50)
            input("\nTryck på [Enter] för att återgå till menyn...")


if __name__ == "__main__":
    try:
        main_cli_loop()
    except KeyboardInterrupt:
        print("\n\nAvbrutet av användaren. Hejdå!")
        sys.exit(0)
