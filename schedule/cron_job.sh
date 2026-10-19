#!/usr/bin/env bash
# ==============================================================================
# GCC Social Listening Pipeline - Scheduled Cron Job
# Idempotent execution script with file-locking and structured failure logging.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOCK_FILE="/tmp/gcc_social_listening_pipeline.lock"
LOG_FILE="$PROJECT_ROOT/logs/cron_run.log"

mkdir -p "$PROJECT_ROOT/logs"

echo "==========================================================" >> "$LOG_FILE"
echo "Starting scheduled pipeline run: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$LOG_FILE"

# Ensure only one instance of the pipeline runs at a time (Idempotency Guard)
exec 200>"$LOCK_FILE"
if ! flock -n 200; then
    echo "[WARNING] Another instance of the pipeline is currently executing. Exiting." >> "$LOG_FILE"
    exit 0
fi

# Locate Python virtual environment
PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

cd "$PROJECT_ROOT"

# Run the complete pipeline
EXIT_CODE=0
"$PYTHON_BIN" run_pipeline.py --all >> "$LOG_FILE" 2>&1 || EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "[CRITICAL] Pipeline execution failed with exit code $EXIT_CODE at $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$LOG_FILE"
    # Write alert log entry
    echo "{\"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\", \"severity\": \"CRITICAL\", \"stage\": \"cron_scheduler\", \"message\": \"Pipeline cron job exited with code $EXIT_CODE\"}" >> "$PROJECT_ROOT/logs/alerts.log"
    exit $EXIT_CODE
else
    echo "[SUCCESS] Pipeline run finished successfully at $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$LOG_FILE"
fi
