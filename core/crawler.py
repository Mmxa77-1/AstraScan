# core/crawler.py
import asyncio
import aiohttp
import re
import requests
from urllib.parse import urljoin, urlparse
from core.tor_manager import TorManager
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
]

tor = TorManager()


def clean_url(url: str) -> str:
    return url.split("#")[0].rstrip("/")


def extract_links(base_url, html):
    urls = set()
    pattern = r'href=["\'](.*?)["\']'
    matches = re.findall(pattern, html, re.IGNORECASE)

    for link in matches:
        full = urljoin(base_url, link)
        parsed_base = urlparse(base_url)
        parsed = urlparse(full)
        if parsed.netloc == parsed_base.netloc:
            urls.add(clean_url(full))

    return urls


# -------------------------------
# ASYNC FETCH
# -------------------------------
async def fetch_async(url, session):
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    try:
        async with session.get(url, headers=headers, timeout=10) as resp:
            if resp.status != 200:
                print(f"[DEBUG] Async fetch non-200 {url}: {resp.status}")
                return None
            return await resp.text()
    except Exception as e:
        print(f"[DEBUG] Async fetch error {url}: {e}")
        return None


# -------------------------------
# TOR FETCH
# -------------------------------
def fetch_tor(url):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    resp = tor.request(url, headers=headers, timeout=18)

    if resp and resp.status_code == 200:
        return resp.text

    print(f"[DEBUG] Tor fetch error {url}")
    return None


# -------------------------------
# REQUESTS FALLBACK FETCH
# -------------------------------
def fetch_requests(url):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        r = requests.get(url, headers=headers, timeout=10, verify=True)
        if r.status_code == 200:
            return r.text
    except Exception as e:
        print(f"[DEBUG] Requests fetch error {url}: {e}")
    return None


# -------------------------------
# MASTER CRAWLER
# -------------------------------
async def crawl_website(start_url, max_pages=50, use_tor=False, refresh_tor=False):
    visited = set()
    to_visit = {clean_url(start_url)}
    pages = {}

    print("[DEBUG] Starting crawler")

    # Start async session
    async with aiohttp.ClientSession() as session:
        while to_visit and len(pages) < max_pages:

            url = to_visit.pop()
            if url in visited:
                continue

            visited.add(url)
            print(f"[DEBUG] Visiting: {url}")

            # OPTIONAL — Refresh Tor identity
            if use_tor and refresh_tor:
                print("[TOR] Refreshing identity...")
                tor.renew_identity()
                print("[TOR] New IP:", tor.get_ip())

            html = None

            # Priority 1 — Tor fetch
            if use_tor:
                html = fetch_tor(url)

            # Priority 2 — Async aiohttp
            if html is None and not use_tor:
                html = await fetch_async(url, session)

            # Priority 3 — fallback to requests
            if html is None:
                print("[DEBUG] Falling back to requests...")
                html = fetch_requests(url)

            if html is None:
                print(f"[DEBUG] Failed: {url}")
                continue

            pages[url] = html

            # Extract internal links
            new_links = extract_links(url, html)
            for link in new_links:
                if link not in visited:
                    to_visit.add(link)

    print(f"[DEBUG] Finished crawling: {len(pages)} pages")
    return pages
