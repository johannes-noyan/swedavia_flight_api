# Logbook - Swedavia Flight API

**Name:** Johannes Noyan \
**Team members:** Johannes Noyan, Ali Cay, Juan Martin \
**Group name:** Grupp2 \
**Email:** johannes_noyan@outlook.com \
**Submitting:** Project - Swedavia Flight API

---

## Work log

<!-- 
Work log:
### yyyy-mm-dd

**Worked with:**

**What was done:**

**Problems and solutions:**

**Decisions:**

**References:**
 -->

 ### 2026-06-01

**Worked with:**
* We began working with "Part 1: Research and planning".

**What was done:**
* I watched "Buster Swedavia FlightInfo API v2 .mov".
* I read the assignment instructions of "Kopia av 4. Reverse Engineer
  a Result (1).sh"
* We decided to recreate "Swedavia Flight API" application with reverse
  engineering.
* I setup my Git respiratory and Github.
* My first "git commit -m" was done.
* I answered the questions from "Step 2: Ask Questions".
* I answered the questions from "Step 3 → 5: Guess the Inputs, Guess
  the Process, Sketch the Steps".
* We completed "Part 1: Research and planning".
* My second "git commit -m" was done.

**Problems and solutions:** \
No problems or solutions.

**Decisions:** \
No Decisions.

**References:**
* "Buster Swedavia FlightInfo API v2 .mov"
* "Kopia av 4. Reverse Engineer a Result (1).sh"
* https://aistudio.google.com/
* https://copilot.microsoft.com/shares/x3hVi3naxZPyUGsXiJrAp
* https://copilot.microsoft.com/shares/Lgsrf8rW1gE9hazKbvsq7

--

## Part 1: Research and planning
* We decided to recreate "Swedavia Flight API" application with reverse
  engineering.
* Configured Git:
  * Name: Johannes Noyan
  * Email: johannes_noyan@outlook.com
* Initialized my repository with "git init" with the following folder
  structure: screenshot/, scripts/, data/, results/.
* I created the signature scripts: signature.sh, signagure.ps1.
* I setup my Git respiratory and Github. The name of the respiratory
  is "swedavia_flight_api".
* My first "git commit" was:
  * "initial commit: repo structure and logbook template"

### Step 2: Ask Questions

### What kind of data is this?
The data is from "Swedavia FlightInfo API v2" and it displays real time 
flight data of 10 Swedavia airports allocated in Sweden. The flight data
is about arrivals, departures, information about the flights.

To find destination statistics, you need to go to Swedavia website,
because "Swedavia FlightInfo API v2" does not have this information.

### What could have created this?
It looked like it was created with the Python programming language,
"Swedavia FlightInfo API v2", some kind of AI.


### Answer from Gemini 3 Flash Preview:

Based on the document provided, here are the answers to your questions:

### 1. What kind of data does the application have?
The application processes **real-time flight data** sourced from the
"Swedavia FlightInfo API v2." Specifically, it contains:

* **Airport Information:** Data for 10 specific Swedavia airports in
  Sweden (Stockholm Arlanda, Göteborg Landvetter, Stockholm Bromma,
  Malmö, Luleå, Umeå, Östersund, Visby, Ronneby, and Kiruna).
* **Flight Details:** 
  * **Arrivals and Departures:** Flight numbers and the airlines
    operating them.
  * **Route Info:** Origin and destination cities/IATA codes.
  * **Status & Logistics:** Real-time status (e.g., Scheduled,
    Departed), terminal numbers, gate assignments, and baggage belt
    information.
  * **Timing:** Scheduled, Estimated, and Actual times in both UTC
    and CET.
  * **Classification:** Domestic/International (D/I) markers and
    special remarks (e.g., actual departure time).
* **Geographic Mapping:** It uses a `city_country.json` file,
  suggesting it maps airport codes to specific cities and countries.
* **System Health:** "HeartBeat" data used to check the health and
  connectivity of the API.

**Note:** The application specifically **does not** have destination
statistics; the document mentions you must visit the Swedavia website
for that information.

### 2. What could have created the application?
The application was created using the following technologies and
structures:

* **Programming Language:** **Python**. This is confirmed by the file
  extensions (`.py`) and the terminal menu header which identifies it
  as a "Python-klient."
* **External API:** The **Swedavia FlightInfo API v2**. The application
  acts as a client wrapper for this official Swedish airport data
  source, utilizing its OData query endpoints.
* **Data Formats:** It likely uses **JSON** for data handling
  (indicated by `city_country.json`) and **OData** protocol for
  advanced queries.
* **Development Components:**
  * **Modular Code:** The file list (`airport.py`, `destinationer.py`)
    suggests a structured approach where different functionalities
    (airport handling vs. destination mapping) are separated into
    different modules.
  * **Documentation:** The presence of `README.md` and `FÖRKLARING.md`
    indicates a documented development process, likely intended for
    other users or developers to understand how to run the client.
* **Interface Type:** A **CLI (Command Line Interface)**. It is a
  terminal-based application designed for user interaction through
  text menus and keyboard inputs.

### Step 2: End here

### Step 3 → 5: Guess the Inputs, Guess the Process, Sketch the Steps

### What inputs would you need to get this result? What functions or logic might build this?
1. Full project description, I will upload the following files to
   Gemini:
   * high_level_system_instructions.txt, project_overview.txt,
     technical_requirements.txt, menu_terminal_interface.txt,
     api_details.txt, destinations-statistik-2025.csv,
     documentation_files.txt
2. Output format, tell Gemini:
  * "All code and comments must be in English. All user-facing text
    (terminal UI, prompts, messages) must be in Swedish.Use the content
    of destinations-statistik-2025.csv to create city_country.json.
    Output the entire project as downloadable code blocks, one file
    per block. Each code block must clearly specify the filename in
    a comment at the top or in the code fence label.
    
    Generate all necessary files (airport.py, destinationer.py,
    city_country.json content, any helper scripts if needed,
    README.md, FÖRKLARING.md) in this format."

### Step 3 → 5: Ends here

* My second "git commit" was:
  * "Complete part 1: Research and planning"

## Part 2: Start of work (Implementation / Execution)





## Part 3: Completion of work (Finalization & improvement)

## Part 4 - Conclusion
