import os
import json
from datetime import datetime

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AstraScan Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
        h1 {{ text-align: center; }}
        table {{ width: 90%; margin: 20px auto; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background-color: #007BFF; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .xss {{ color: red; font-weight: bold; }}
        .sqli {{ color: orange; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>AstraScan Report</h1>
    <p style="text-align:center;">Generated at: {generated_at}</p>

    <h2>Top Targets</h2>
    <table>
        <tr><th>URL</th><th>Score</th></tr>
        {top_targets_rows}
    </table>

    <h2>Findings</h2>
    <table>
        <tr><th>URL</th><th>Parameter</th><th>Type</th><th>Payload</th></tr>
        {findings_rows}
    </table>
</body>
</html>
"""

def generate_report(json_path="reports/ai_results.json", output_path="reports/ai_report.html"):
    if not os.path.exists(json_path):
        print(f"[!] JSON file not found: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f).get("results", {})

    generated_at = datetime.utcnow().isoformat() + "Z"

    # Top targets table
    top_targets_rows = ""
    for url, score in data.get("top_targets", []):
        top_targets_rows += f"<tr><td>{url}</td><td>{score:.2f}</td></tr>"

    # Findings table
    findings_rows = ""
    for f in data.get("findings", []):
        type_class = f.get("type", "").lower()
        payload = f.get("payload", "")
        findings_rows += f"<tr class='{type_class}'><td>{f.get('url')}</td><td>{f.get('param')}</td><td>{f.get('type')}</td><td>{payload}</td></tr>"

    html_content = HTML_TEMPLATE.format(
        generated_at=generated_at,
        top_targets_rows=top_targets_rows,
        findings_rows=findings_rows
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[+] HTML report generated: {output_path}")
