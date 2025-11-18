import json, os
from datetime import datetime

def save_results(results: dict, path="reports/ai_results.json"):
    out = {
        "meta": {"generated_at": datetime.utcnow().isoformat() + "Z"},
        "results": results
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
