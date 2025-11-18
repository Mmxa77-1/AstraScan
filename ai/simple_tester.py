import aiohttp
from urllib.parse import urlencode

HEADERS = {"User-Agent": "AstraScan/1.0"}

async def run_conservative_tests(url, params, xss_payloads, sqli_payloads):
    if not params:
        return []
    findings = []
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        for param in params:
            for payload in xss_payloads:
                test_url = f"{url}?{urlencode({param: payload})}"
                try:
                    async with session.get(test_url, timeout=5) as r:
                        text = await r.text()
                        if payload in text:
                            findings.append({"url": url, "param": param, "type": "xss"})
                except:
                    continue
            for payload in sqli_payloads:
                test_url = f"{url}?{urlencode({param: payload})}"
                try:
                    async with session.get(test_url, timeout=5) as r:
                        text = await r.text()
                        if any(err in text.lower() for err in ["mysql", "syntax error", "sql"]):
                            findings.append({"url": url, "param": param, "type": "sqli"})
                except:
                    continue
    return findings
