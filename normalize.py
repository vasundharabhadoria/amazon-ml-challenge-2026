import re
from unidecode import unidecode

# ---- Legal suffix normalization dictionary ----
# Map common variants to a single canonical short form
SUFFIX_MAP = {
    r'\bprivate limited\b': 'pvt ltd',
    r'\bprivate\b': 'pvt',
    r'\blimited\b': 'ltd',
    r'\bcorporation\b': 'corp',
    r'\bincorporated\b': 'inc',
    r'\bcompany\b': 'co',
    r'\bllp\b': 'llp',
    r'\bllc\b': 'llc',
    r'\band\b': '&',
}

# Address abbreviation normalization
ADDRESS_MAP = {
    r'\broad\b': 'rd',
    r'\bstreet\b': 'st',
    r'\bavenue\b': 'ave',
    r'\bdrive\b': 'dr',
    r'\bboulevard\b': 'blvd',
    r'\blane\b': 'ln',
    r'\bapartment\b': 'apt',
    r'\bfloor\b': 'fl',
    r'\bsaint\b': 'st',  # careful: also matches "st" for street; order/context matters, refine later
}

DOMAIN_PATTERN = re.compile(r'\.(com|in|org|net|co)\b')
HANDLE_PATTERN = re.compile(r'^@')
FORMERLY_PATTERN = re.compile(r'formerly[:\s]*', flags=re.IGNORECASE)
NON_ALNUM = re.compile(r'[^a-z0-9\s&]')
MULTI_SPACE = re.compile(r'\s+')


def transliterate(text: str) -> str:
    """Convert any non-Latin script to a consistent ASCII phonetic representation."""
    if text is None:
        return ""
    return unidecode(str(text))


def extract_formerly_name(name: str) -> str:
    """
    If name contains 'formerly: X', extract X (the old name) since that's
    what's likely to match S1. Returns the extracted name if pattern found,
    else returns the original name unchanged.
    """
    match = re.search(r'formerly[:\s]*(.+)$', name, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return name


def clean_domain_or_handle(name: str) -> str:
    """
    Convert domain-style or handle-style names into space-separated tokens.
    e.g. 'bnpgroupcompaniesdelhi.com' -> 'bnp group companies delhi' (approx —
    true word-segmentation of concatenated domains is hard; at minimum strip
    the domain suffix and @ so remaining tokens can still match).
    """
    name = HANDLE_PATTERN.sub('', name)
    name = DOMAIN_PATTERN.sub('', name)
    return name


def apply_suffix_map(text: str, mapping: dict) -> str:
    for pattern, replacement in mapping.items():
        text = re.sub(pattern, replacement, text)
    return text


def normalize_business_name(name: str) -> str:
    if name is None or (isinstance(name, float)):  # handles NaN
        return ""
    name = str(name)

    # 1. Extract "formerly" name if present (do this before other cleaning)
    name = extract_formerly_name(name)

    # 2. Transliterate non-Latin scripts
    name = transliterate(name)

    # 3. Lowercase
    name = name.lower()

    # 4. Strip domain suffixes / @ handles
    name = clean_domain_or_handle(name)

    # 5. Normalize legal suffixes/abbreviations
    name = apply_suffix_map(name, SUFFIX_MAP)

    # 6. Remove punctuation except & (keep as separator signal), collapse whitespace
    name = NON_ALNUM.sub(' ', name)
    name = MULTI_SPACE.sub(' ', name).strip()

    return name


def normalize_address(address: str) -> str:
    if address is None or (isinstance(address, float)):
        return ""
    address = str(address)

    address = transliterate(address)
    address = address.lower()
    address = apply_suffix_map(address, ADDRESS_MAP)
    address = NON_ALNUM.sub(' ', address)
    address = MULTI_SPACE.sub(' ', address).strip()

    return address


def normalize_country(country: str) -> str:
    if country is None or (isinstance(country, float)):
        return ""
    return str(country).strip().lower()