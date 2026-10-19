"""
Alert Manager and Structured Logging for the GCC Social Listening Pipeline.
Implements log-based failure alerting, idempotency verification, and alert dispatching.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
from config import settings

logger = logging.getLogger(__name__)


class AlertManager:
    """
    Log-based failure alerting with structured JSON records.
    Writes high-priority incidents to logs/alerts.log and standard pipeline logs.
    """

    def __init__(self, alert_log_file: Optional[Path] = None):
        self.alert_log_file = alert_log_file or settings.ALERT_LOG_FILE
        self.alert_log_file.parent.mkdir(parents=True, exist_ok=True)

    def trigger_alert(
        self,
        severity: str,
        stage: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record a structured alert to the alert log.

        Args:
            severity: "INFO", "WARNING", "ERROR", "CRITICAL"
            stage: Pipeline stage ("ingestion", "storage", "processing", "validation")
            message: Human-readable alert summary
            details: Contextual metadata (error message, trace, counts)
        """
        now = datetime.now(timezone.utc).isoformat()
        alert_payload = {
            "timestamp": now,
            "severity": severity.upper(),
            "stage": stage,
            "message": message,
            "details": details or {},
        }

        # Format as single-line JSON log entry for ingestion by CloudWatch/Datadog/Elastic
        log_line = json.dumps(alert_payload, ensure_ascii=False)

        # Append to alerts log file
        with open(self.alert_log_file, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

        # Emit to console / standard logger
        if severity.upper() in ("ERROR", "CRITICAL"):
            logger.error(f"🚨 [PIPELINE ALERT - {severity.upper()}] [{stage}]: {message}")
        elif severity.upper() == "WARNING":
            logger.warning(f"⚠️ [PIPELINE ALERT - {severity.upper()}] [{stage}]: {message}")
        else:
            logger.info(f"ℹ️ [PIPELINE INFO] [{stage}]: {message}")

        return alert_payload

    def info(self, stage: str, message: str, **kwargs):
        return self.trigger_alert("INFO", stage, message, kwargs)

    def warning(self, stage: str, message: str, **kwargs):
        return self.trigger_alert("WARNING", stage, message, kwargs)

    def error(self, stage: str, message: str, **kwargs):
        return self.trigger_alert("ERROR", stage, message, kwargs)

    def critical(self, stage: str, message: str, **kwargs):
        return self.trigger_alert("CRITICAL", stage, message, kwargs)


# Global singleton instance
alert_manager = AlertManager()
