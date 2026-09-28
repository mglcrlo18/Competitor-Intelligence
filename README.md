# Competitor Intelligence Tool

An enterprise-grade, automated competitor intelligence and strategic decision-support platform engineered for GoNano leadership, regional directors, and commercial sales teams.

---

## Key Capabilities

1. **Dual-Layer Operational Database:**
   * SQLite ACID relational engine indexing 68 monitored competitors, domain footprints, patent registries, and historical threat signals.
   * Bidirectional synchronization with the live [Competitor Report Tracker](https://docs.google.com/spreadsheets/d/1FfQwtbauwbzFXLqmNmaaktAge4ts9wXihqVaeT0JGB0/edit?usp=sharing).

2. **2D Threat vs. Friction Matrix:**
   * Statistical multi-factor scoring evaluating competitor market presence, capital backing, advertising aggression, and product viability.
   * Dealer friction rate modeling contractor defection propensity, supply chain stockouts, and warranty dispute frequencies.

3. **Frontline Sales Enablement:**
   * Dynamic Sales Battlecards with competitor pricing tables, warranty landmines, and trap questions for commercial bids.
   * Marketing Reality Gap engine deconstructing rival advertising claims against empirical ASTM laboratory testing.

4. **Autonomous Bi-Daily Briefings:**
   * Silent headless email dispatch at **9:00 PM PHT (21:00)** and **00:00 H PHT (Midnight)**.
   * Sends clean, 1-page executive memos directly over TLS SMTP without launching native mail applications.
   * Built-in CC distribution support for C-level leadership.

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/competitor-intelligence.git
cd competitor-intelligence
```

### 2. Configure Environment
Copy the example environment template and add your credentials:
```bash
cp .env.example .env
```
Edit `.env` with your parameters:
```env
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_16_character_app_password
RECIPIENT_EMAIL=your_email@gmail.com
CC_EMAILS=officer1@gonano.ca, officer2@gonano.ca
```

### 3. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run the Platform

**Interactive Dashboard:**
```bash
streamlit run app.py
```

**Run QA Test Suite:**
```bash
python test_qa_suite.py
```

**Dispatch Immediate Executive Briefing:**
```bash
python scheduled_briefing_runner.py
```

---

## Architecture

```
[OSINT Ingestion]           [Field Tracker]
  Google News RSS             Google Sheets API
         \                           /
          v                         v
    +-------------------------------------+
    |  SQLite Relational Database (ACID)  |
    +-------------------------------------+
          |                         |
          v                         v
  [Streamlit Dashboard]     [Headless SMTP Runner]
  - 2D Strategic Matrix     - 9:00 PM / 00:00 H PHT
  - Sales Battlecards       - 1-Page Executive Memo
```

---

## License & Confidentiality
CONFIDENTIAL // Strictly for GoNano internal commercial operations and authorized leadership distribution.
