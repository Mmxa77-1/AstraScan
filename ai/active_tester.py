# ai/simple_tester.py
import aiohttp
import asyncio
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

HEADERS = {"User-Agent": "AstraScan/1.0"}

async def do_get(session, url):
    try:
        async with session.get(url, timeout=6) as r:
            text = await r.text()
            return r.status, text
    except Exception:
        return None, None

async def run_conservative_tests(base_url, params, xss_payloads, sqli_payloads):
    """
    For each param, inject a small set of conservative payloads and look for reflections / sql errors.
    Returns list of findings (tuples or dicts).
    """
    findings = []
    if not params:
        return findings

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = []
        for p in params:
            for payload in xss_payloads:
                # build URL with single param injection
                parsed = urlparse(base_url)
                q = dict(parse_qsl(parsed.query))
                q[p] = payload
                new_q = urlencode(q)
                new_url = urlunparse(parsed._replace(query=new_q))
                tasks.append(do_get(session, new_url))
            for payload in sqli_payloads:
                parsed = urlparse(base_url)
                q = dict(parse_qsl(parsed.query))
                q[p] = payload
                new_q = urlencode(q)
                new_url = urlunparse(parsed._replace(query=new_q))
                tasks.append(do_get(session, new_url))
        results = await asyncio.gather(*tasks)
        # simple passive checks
        idx = 0
        for p in params:
            for _ in xss_payloads:
                status, body = results[idx]
                idx += 1
                if body and "<script>alert(1)" in body:
                    findings.append({"url": base_url, "param": p, "type": "reflected_xss"})
            for _ in sqli_payloads:
                status, body = results[idx]
                idx += 1
                if body and any(k in body.lower() for k in ["sql syntax", "mysql", "syntax error", "sqlite3"]):
                    findings.append({"url": base_url, "param": p, "type": "sql_error_evidence"})
    return findings
