from urllib.parse import urlparse, parse_qs
import re

def extract_forms(html):
    forms = []
    matches = re.findall(r'<form[^>]*>(.*?)</form>', html, re.DOTALL|re.IGNORECASE)
    for form in matches:
        inputs = re.findall(r'<input[^>]*name=["\'](.*?)["\']', form, re.IGNORECASE)
        forms.append({"inputs": inputs})
    return forms

def find_parameters(url, html=None):
    results = set()
    parsed = urlparse(url)
    get_params = parse_qs(parsed.query)
    for p in get_params.keys():
        results.add(p)
    if html:
        forms = extract_forms(html)
        for form in forms:
            for input_name in form["inputs"]:
                results.add(input_name)
    return list(results)
