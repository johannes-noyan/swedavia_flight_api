# Swedavia Flight API Client

This project is a standalone Python 3 terminal application that interacts with the **Swedavia Flightinfo API v2** to display real-time flight data for Sweden’s 10 Swedavia airports. 

It provides Swedish terminal outputs, user prompts, and menus, while keeping internal code logic and comments fully in English.

## Key Features

- **Standard REST Integration**: Integrates directly with Swedavia’s official developer endpoints supporting arrivals, departures, custom searches, and heartbeat requests.
- **Robust Simulated Sandbox**: If no API key is supplied, the application automatically boots into a high-fidelity simulation engine that generates realistic flight statistics and models matching the true Swedavia API structure.
- **Offline Country Mapping**: Uses a local JSON-based mapping lookup table (`city_country.json`) computed from official 2025 passenger statistics to analyze and associate destination cities to their respective countries with zero overhead.
- **Unified Analysis Engine**: Includes a statistics model (`destinationer.py`) that lists flight concentrations by country/city and supports advanced search filters.

---

## File Structure

- **`airport.py`**: The primary executable terminal application, providing navigation loops, inputs, formatting cards, pagination, and response handlers.
- **`destinationer.py`**: A helper module loaded to compute flight counts, handle city-to-country lookups, and format stats tables.
- **`city_country.json`**: An offline database matching 263 international cities to their respective countries.
- **`README.md`**: Project guidance (This file, written in English).
- **`FÖRKLARING.md`**: User-facing walkthrough (written in Swedish).

---

## Installation & Getting Started

### 1. Requirements

The client requires **Python 3.6+** and the `requests` library for active web integrations.

### 2. Install Dependencies

You can install the official HTTP fetching library using `pip`:

```bash
pip install requests
```

*Note: The application has a automatic fallback. If `requests` is missing from your system, it can still run under the fully interactive offline Simulation Sandbox.*

### 3. Setting Your Swedavia API Key

To query live Swedish arrivals/departures, create a free account on the [Swedavia Developer Portal](https://developer.swedavia.se/) to receive your Subscription Key.

Assign the subscription key to the `SWEDAVIA_API_KEY` environment variable in your terminal:

**On Linux/macOS:**
```bash
export SWEDAVIA_API_KEY="your_actual_subscription_key_here"
```

**On Windows (Command Prompt):**
```cmd
set SWEDAVIA_API_KEY="your_actual_subscription_key_here"
```

**On Windows (PowerShell):**
```powershell
$env:SWEDAVIA_API_KEY="your_actual_subscription_key_here"
```

*If this environment variable is omitted or blank, `airport.py` executes in simulation mode with mock flights.*

---

## How to Run

Launch the primary application from your terminal:

```bash
python airport.py
```

---

## Interactive Menu Overview

Once started, the CLI offers an interactive main menu representing Swedavia's raw and computed features:

1. **Ankomster (Arrivals)**: Returns incoming flights for any of the 10 Swedish Swedavia airports (such as ARN, GOT, BMA, VBY) for a chosen date (or keywords like `nu`/`idag`, `imorgon`, `igår`). Displays scheduled, estimated, actual times in UTC and Sweden local formats (CET/CEST), gates, terminals, status, and baggage belts.
2. **Avgångar (Departures)**: Displays outgoing flights with option to filter out already departed planes. Shows destination cities, terminals, and gates.
3. **Sök specifikt flightnummer**: Performs a target query to find matching flights for a specific airline number (e.g., `SK532` or `LH819`).
4. **OData-förfrågan**: Queries Swedavia with custom query expressions using the OData filter protocol.
5. **HeartBeat**: Checks endpoint server availability.
6. **Demonstrera alla endpoints**: Runs automated sequential API request sequences to check health, query test flights, and evaluate formats.
