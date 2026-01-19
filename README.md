# ActiveSGMetrics

**ActiveSGMetrics** is a soon to be full-stack data engineering and analytics project designed to scrape, store, and analyze real-time gym occupancy rates from ActiveSG facilities.

The goal is to build a historical dataset of gym occupancy rates and analyze them :D

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)
![Playwright](https://img.shields.io/badge/Playwright-Scraper-orange.svg)
![SQLModel](https://img.shields.io/badge/SQLModel-Database-blue)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)


## Architecture

The project consists of three main components:

1.  **Scraper Service (`/services/scraper`)**:
    * Built with **Playwright** (Python) to handle dynamic JavaScript content on the ActiveSG portal.
    * Runs automatically via **GitHub Actions** (Dispatch/CRON).
    * Includes a **"Wake Up" mechanism** to ensure the backend is online before data ingestion.
2.  **Backend API (`/backend`)**:
    * Built with **FastAPI**.
    * Handles data ingestion (`/ingestdata`), validation, and retrieval.
    * Uses **SQLModel** (SQLAlchemy + Pydantic) for ORM and type safety.
3.  **Database**:
    * **PostgreSQL** (hosted on Supabase).
    * Schema management via **Alembic** migrations.
    * Stores `GymMetaData` (names, IDs) and `GymOccupancyData` (historical capacity %, timestamped).

## Features

* **Automated Scraping**: Fetches real-time capacity for all ActiveSG gyms.
* **Resilient Ingestion**: Scraper includes retry logic, user-agent rotation, and health checks to prevent data loss.
* **Historical Tracking**: Stores timestamped occupancy data (with timezone support) to enable trend analysis.
* **Modern Stack**: Fully typed Python codebase using Pydantic and SQLModel.


## Installation & Setup

### Prerequisites
* Python 3.10+
* A PostgreSQL Database (e.g., Supabase)

### 1. Clone the Repository
```bash
git clone [https://github.com/ZadeNova/ActiveSGMetrics.git](https://github.com/ZadeNova/ActiveSGMetrics.git)
cd ActiveSGMetrics
```
### 2. Set up environment variables

```bash
# Database Connection (Supabase Transaction Pooler recommended)
SUPABASE_DATABASE_URL="postgresql://user:password@host:port/dbname"

# URLs for Scraper
WEBSITE_URL="https://[ACTIVESG_URL_HERE]"
LOCAL_BACKEND_URL="http://localhost:8000"
PROD_BACKEND_URL="https://[YOUR_PROD_URL]"

# Optional: Toggle for local vs prod
GITHUB_ACTIONS="false"
```

### 3. Install dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Chunk 5: Project Structure & License

```markdown
## 📂 Project Structure

```text
ActiveSGMetrics/
├── .github/workflows/   # GitHub Actions (CI/CD)
├── backend/             # FastAPI Application
│   ├── migrations/      # Alembic database migrations
│   ├── models/          # SQLModel database tables (GymMetaData, GymOccupancyData)
│   ├── routers/         # API Endpoints (ingest, health, data)
│   ├── schemas/         # Pydantic data schemas
│   ├── services/        # Backend logic services
│   ├── database.py      # DB connection logic
│   └── main.py          # App entry point
├── services/scraper/    # Scraper Logic
│   └── main_scraper.py  # Playwright script
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

This project is licensed under the MIT License - see the LICENSE file for details.


