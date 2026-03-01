import boto3

class Logs:
    def __init__(self, log_group: str):
        self.log_group = log_group
        self.logs = boto3.client("logs")

    """
    Records an INFO-level log.
    """
    def info(self, message: str, **context):
        self._log("INFO", message, context)

    """
    Records an ERROR-level log.
    """
    def error(self, message: str, **context):
        self._log("ERROR", message, context)

    def _log(self, level: str, message: str, context: dict):
        self.logs.put_log_events(
            logGroupName=self.log_group,
            logStreamName="default",
            logEvents=[{"timestamp": _now_ms(), "message": _format(level, message, context)}],
        )

"""
Returns the current timestamp, in milliseconds.
"""
def _now_ms() -> int:
    from datetime import datetime, timezone
    return int(datetime.now(timezone.utc).timestamp() * 1000)

"""
Formats a message to include as "context" in a log, for instance:
order_id=42, email=abc@xyz -> (order_id=42, email=abc@xyz)
"""
def _format(level: str, message: str, context: dict) -> str:
    base = f"{level} {message}"
    if not context:
        return base
    pairs = ", ".join(f"{k}={v}" for k, v in context.items())
    return f"{base} ({pairs})"
