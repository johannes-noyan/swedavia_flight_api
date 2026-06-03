# -*- coding: utf-8 -*-
"""
destinationer.py

This module provides helper utilities for destination statistics and country mapping.
It maps cities to countries using the local 'city_country.json' database and lists unique destinations.
It is intended for Swedish users; hence the CLI interface is in Swedish while the code and comments are in English.
"""

import os
import json

def load_city_country_map():
    """
    Loads city to country mapping from the city_country.json file.
    Resolves the file location relative to this script for robustness.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'city_country.json')
    
    if not os.path.exists(json_path):
        # Fallback if run without correct directory structure or empty
        return {}
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def lookup_country(city, mapping=None):
    """
    Looks up the country for a given city in a case-insensitive and robust way.
    Handles compound names (e.g., 'London LHR' -> 'London').
    """
    if not city:
        return "Okänt land"
        
    if mapping is None:
        mapping = load_city_country_map()
        
    # Standardize the city input
    city_clean = city.strip()
    
    # Direct match first (case-insensitive)
    for k, v in mapping.items():
        if k.lower() == city_clean.lower():
            return v
            
    # Remove airport codes if present in airport string e.g., "London LHR" or "London (LHR)" or "Frankfurt Apt"
    # Take first word or major parts
    parts = city_clean.replace('(', ' ').replace(')', ' ').split()
    if len(parts) > 1:
        # Try matching progressive prefixes
        for i in range(len(parts), 0, -1):
            sub_city = " ".join(parts[:i])
            for k, v in mapping.items():
                if k.lower() == sub_city.lower():
                    return v
                    
    # Try searching for substring
    for k, v in mapping.items():
        if k.lower() in city_clean.lower() or city_clean.lower() in k.lower():
            return v
            
    return "Okänt land"

def generate_destination_stats(flights, is_arrival=True, city_filter=None, country_filter=None):
    """
    Analyzes flight data and aggregates statistics grouped by city and country.
    
    - flights: List of parsed flight dictionaries.
    - is_arrival: True if analyzing arrivals (origination), False if departures (destination).
    - city_filter: Optional Swedish city filter string.
    - country_filter: Optional Swedish country filter string.
    
    Returns a sorted list of dictionaries containing:
      {
         'city': City Name,
         'country': Country Name,
         'count': Number of flights,
         'percentage': Percentage of total analyzed flights
      }
    """
    mapping = load_city_country_map()
    stats = {}
    total_valid_flights = 0
    
    for fl in flights:
        # In Arrivals, we look at the origin city.
        # In Departures, we look at the destination city.
        city = fl.get('from_city' if is_arrival else 'to_city', 'Okänd stad')
        if not city or city == 'N/A' or city == '(tom)':
            continue
            
        # Clean city name e.g. "Paris CDG" -> "Paris"
        display_city = city
        country = lookup_country(display_city, mapping)
        
        # Apply filters (case-insensitive)
        if city_filter and city_filter.strip().lower() not in display_city.lower():
            continue
        if country_filter and country_filter.strip().lower() not in country.lower():
            continue
            
        key = (display_city, country)
        stats[key] = stats.get(key, 0) + 1
        total_valid_flights += 1
        
    result = []
    for (city, country), count in stats.items():
        percentage = (count / total_valid_flights * 100) if total_valid_flights > 0 else 0
        result.append({
            'city': city,
            'country': country,
            'count': count,
            'percentage': round(percentage, 1)
        })
        
    # Sort by count desc, then city asc
    result.sort(key=lambda x: (-x['count'], x['city'].lower()))
    return result, total_valid_flights

def display_stats_cli(stats, total_flights, is_arrival=True, city_filter=None, country_filter=None):
    """
    Prints a beautifully formatted, Swedish terminal-friendly table mapping
    destination statistics.
    """
    header_title = "ANKOMSTSTATISTIK (URSPRUNG)" if is_arrival else "AVGÅNGSSTATISTIK (DESTINATION)"
    
    print("\n" + "=" * 60)
    print(f" {header_title}")
    print("=" * 60)
    
    if city_filter:
        print(f"Filter stadsnamn: '{city_filter}'")
    if country_filter:
        print(f"Filter land: '{country_filter}'")
    if city_filter or country_filter:
        print("-" * 60)
        
    if not stats:
        print("Inga matchande destinationer hittades för de laddade flygen.")
        print("=" * 60)
        return
        
    print(f"{'STAD':<22} | {'LAND':<22} | {'FLYG':<6} | {'ANDEL':<6}")
    print("-" * 60)
    
    for entry in stats:
        city_disp = entry['city'][:22]
        country_disp = entry['country'][:22]
        print(f"{city_disp:<22} | {country_disp:<22} | {entry['count']:<6} | {entry['percentage']}%")
        
    print("-" * 60)
    print(f"Totalt antal analyserade flygningar: {total_flights}")
    print("=" * 60 + "\n")
