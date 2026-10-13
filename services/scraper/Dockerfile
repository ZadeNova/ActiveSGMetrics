FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps chromium

COPY backend/config.py ./backend/config.py
COPY backend/models/__init__.py ./backend/models/__init__.py
COPY backend/models/gym.py ./backend/models/gym.py
COPY services/scraper/main_scraper.py ./services/scraper/main_scraper.py

ENV PYTHONPATH=/app

CMD ["python", "services/scraper/main_scraper.py"]
