#!/usr/bin/env python3
import argparse
import asyncio
import os

from core.crawler import crawl_website
from core.parser import find_parameters
from ai.detector import AIDetector, extract_features
from ai.prioritizer import prioritize
from ai.payloads import generate_xss_payloads, generate_sqli_payloads
from reports.json_writer import save_results


# ---------------------------------------------------------
# ARGUMENT PARSER
# ---------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="AstraScan - AI Powered Web Scanner")

    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("--active", action="store_true", help="Enable active vulnerability testing")
    parser.add_argument("--max-pages", type=int, default=50, help="Max pages to crawl")
    parser.add_argument("--top", type=int, default=20, help="Top N URLs to score")
    parser.add_argument("--tor", action="store_true", help="Route all traffic over Tor")
    parser.add_argument("--tor-refresh", action="store_true",
                        help="Refresh Tor identity before each fetch (requires Tor control port)")

    return parser.parse_args()


# ---------------------------------------------------------
# NORMALIZE INPUT URL
# ---------------------------------------------------------
def normalize_target(target):
    if not target.startswith("http://") and not target.startswith("https://"):
        target = "http://" + target
    return target.rstrip("/")


# ---------------------------------------------------------
# RUN THE FULL SCAN PIPELINE
# ---------------------------------------------------------
async def run_scan(target, active=False, max_pages=50, top_n=20, use_tor=False, refresh_tor=False):

    print(f"[+] Crawling {target} (max_pages={max_pages})")
    if use_tor:
        print("[TOR] Tor mode enabled")
        if refresh_tor:
            print("[TOR] Identity refresh enabled: will cycle Tor IP before each request")

    # Crawl website
    pages = await crawl_website(
        target,
        max_pages=max_pages,
        use_tor=use_tor,
        refresh_tor=refresh_tor
    )

    print(f"[+] Crawled {len(pages)} pages")

    # Extract input parameters
    print("[+] Extracting parameters...")
    params = {url: find_parameters(url, html) for url, html in pages.items()}

    # AI detector
    detector = AIDetector()
    features_map = {}

    for url, html in pages.items():
        feats = extract_features(url, html, params.get(url, []))
        features_map[url] = feats
        detector.add_training_sample(feats)

    # Train model
    trained, msg = detector.train_model()
    print(f"[AI] model train status: {trained} ({msg})")

    # Score all pages
    scores = {url: detector.score(feats) for url, feats in features_map.items()}

    # Sort top targets
    top_targets = prioritize(scores, top_n=top_n)
    print("[AI] Top targets (url, score):")
    for t in top_targets:
        print("  -", t)

    # Optional Active Testing
    findings = []

    if active:
        print("[!] Active tests enabled (permission required!)")
        from ai.simple_tester import run_conservative_tests

        for url, score in top_targets:
            page_params = params.get(url, [])
            xss_payloads = generate_xss_payloads()
            sqli_payloads = generate_sqli_payloads()

            res = await run_conservative_tests(url, page_params, xss_payloads, sqli_payloads)
            if res:
                findings.extend(res)

    # Save report
    output = {
        "target": target,
        "pages_count": len(pages),
        "ai_scores": scores,
        "top_targets": top_targets,
        "findings": findings
    }

    os.makedirs("reports", exist_ok=True)
    save_results(output, path="reports/ai_results.json")
    print("[+] Saved ai_results.json")

    return output


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
async def main_async():
    args = parse_args()
    target = normalize_target(args.url)

    await run_scan(
        target,
        active=args.active,
        max_pages=args.max_pages,
        top_n=args.top,
        use_tor=args.tor,
        refresh_tor=args.tor_refresh
    )


if __name__ == "__main__":
    asyncio.run(main_async())
