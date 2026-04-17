import logging
import sys
from datetime import UTC, datetime


class PipeTextFormatter(logging.Formatter):
    tracked_fields = (
        "request_id",
        "user_id",
        "action",
        "resource_id",
        "provider",
        "duration_ms",
    )

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=UTC).strftime("%Y-%m-%d %H:%M:%S.%f")[
            :-3
        ]
        parts = [timestamp, record.levelname, f"logger={record.name}"]

        for field in self.tracked_fields:
            value = getattr(record, field, None)
            if value is not None:
                parts.append(f"{field}={value}")

        message = record.getMessage().replace("\n", " ").strip()
        parts.append(f"message={message}")
        return " | ".join(parts)


def setup_logging(level: str = "INFO") -> None:
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(PipeTextFormatter())
    root_logger.addHandler(handler)
