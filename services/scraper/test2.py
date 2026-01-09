from datetime import datetime, timezone

timestamp = datetime.now(timezone.utc).isoformat()

print(timestamp)