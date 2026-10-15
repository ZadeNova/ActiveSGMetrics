# ActiveSGMetrics

**ActiveSGMetrics** is a full-stack data engineering and analytics project designed to scrape, store, and analyze real-time gym occupancy rates from ActiveSG facilities.

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
    * Runs automatically via a **systemd timer** on a residential-IP host (Raspberry Pi) — Cloudflare blocks GitHub Actions' shared datacenter IPs, so it can't run there.
    * Writes directly to the database; ingestion isn't exposed as an API endpoint.
2.  **Backend API (`/backend`)**:
    * Built with **FastAPI**.
    * Serves query/analytics endpoints (occupancy history, heatmaps, comparisons) over the scraped data.
    * Uses **SQLModel** (SQLAlchemy + Pydantic) for ORM and type safety.
3.  **Database**:
    * **PostgreSQL** (hosted on Neon).
    * Schema management via **Alembic** migrations.
    * Stores `GymMetaData` (names, IDs) and `GymOccupancyData` (historical capacity %, timestamped).

## Features

* **Automated Scraping**: Fetches real-time capacity for all ActiveSG gyms.
* **Bot-detection-aware**: User-agent rotation and randomized start-time jitter, plus failure-only email alerting if a run ever breaks.
* **Historical Tracking**: Stores timestamped occupancy data (with timezone support) to enable trend analysis.
* **Modern Stack**: Fully typed Python codebase using Pydantic and SQLModel.



This project is licensed under the MIT License - see the LICENSE file for details.


