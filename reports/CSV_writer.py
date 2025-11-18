import csv, os

def save_csv(results, path="reports/ai_results.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "param", "type", "score"])
        for f in results.get("findings", []):
            writer.writerow([f.get("url"), f.get("param"), f.get("type"), f.get("score", "")])
