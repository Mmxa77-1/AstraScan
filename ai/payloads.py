def generate_xss_payloads():
    return ["<xss>", "<script>alert(1)</script>"]

def generate_sqli_payloads():
    return ["'", "' OR '1'='1"]

def encode_payload(p):
    from urllib.parse import quote_plus
    return quote_plus(p)
