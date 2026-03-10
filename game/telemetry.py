import json
from pathlib import Path


class TelemetryStore:
    def __init__(self, path: str = "telemetry.json"):
        self.path = Path(path)
        self.best_score = 0
        self.best_time_ms = None
        self._load()

    def _load(self):
        if not self.path.exists():
            return

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        self.best_score = int(data.get("best_score", 0))
        best_time = data.get("best_time_ms")
        self.best_time_ms = int(best_time) if isinstance(best_time, int) else None

    def _save(self):
        payload = {
            "best_score": self.best_score,
            "best_time_ms": self.best_time_ms,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def update_best_score(self, score: int):
        if score > self.best_score:
            self.best_score = score
            self._save()

    def update_best_time(self, time_ms: int):
        if time_ms < 0:
            return

        if self.best_time_ms is None or time_ms < self.best_time_ms:
            self.best_time_ms = time_ms
            self._save()
