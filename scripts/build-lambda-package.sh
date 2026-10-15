#!/usr/bin/env bash
set -euo pipefail

# Builds a Lambda deployment zip for the FastAPI backend (arm64/Graviton,
# zip deployment not a container image -- see PLANS.md for why). Run
# from anywhere; paths below are resolved relative to the repo root.

cd "$(dirname "$0")/.."

BUILD_DIR="build/lambda"
ZIP_PATH="build/lambda-deployment.zip"

rm -rf "$BUILD_DIR" "$ZIP_PATH"
mkdir -p "$BUILD_DIR"

echo "Installing dependencies for linux/arm64..."
.venv/bin/python -m pip install \
  --platform manylinux2014_aarch64 \
  --implementation cp \
  --python-version 3.12 \
  --only-binary=:all: \
  --target "$BUILD_DIR" \
  -r backend/requirements.txt

echo "Copying application code..."
cp backend/main.py backend/config.py backend/database.py "$BUILD_DIR/"
cp -r backend/models backend/routers backend/schemas backend/services "$BUILD_DIR/"
find "$BUILD_DIR" -name "__pycache__" -type d -prune -exec rm -rf {} +

echo "Zipping..."
(cd "$BUILD_DIR" && zip -rq "../../$ZIP_PATH" .)

echo "Built $ZIP_PATH ($(du -h "$ZIP_PATH" | cut -f1))"
