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



This project is licensed under the MIT License - see the LICENSE file for details.


