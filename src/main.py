"""
ALU Regex Data Extraction & Validation
Author: Student
Description: Reads a text file and uses regex to find
             emails, phone numbers, credit card numbers,
             and currency amounts.
"""

import re
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ── Read the input file ────────────────────────────────────────────────────
with open("input/raw-text.txt", "r", encoding="utf-8") as f:
    text = f.read()

print("File loaded. Starting extraction...\n")


# ══════════════════════════════════════════════════════════════
#  REGEX PATTERNS
#
#  Building blocks used:
#  [abc]       one of these characters
#  [a-z]       any character in this range
#  [^abc]      anything except these characters
#  \d          any digit (0-9)
#  \w          any word character (letter, digit, underscore)
#  \s          any whitespace (space, tab)
#  \b          word boundary
#  .           any single character
#  +           one or more
#  *           zero or more
#  ?           zero or one
#  {n}         exactly n times
#  {n,m}       between n and m times
#  (a|b)       a or b
#  (...)       group
#  ^           start of line
#  $           end of line
# ══════════════════════════════════════════════════════════════


# Email pattern breakdown:
#   [a-zA-Z0-9._+\-]+   one or more valid local-part characters
#   @                    literal @ symbol
#   [a-zA-Z0-9.\-]+      one or more domain characters
#   \.                   literal dot
#   [a-zA-Z]{2,}         TLD — at least 2 letters (com, org, fr, etc.)
EMAIL_PATTERN = r"[a-zA-Z0-9._+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"


# Phone pattern breakdown:
#   \+               literal + sign (international prefix)
#   \d{1,3}          country code: 1 to 3 digits
#   [\s\-.]?         optional separator: space, hyphen, or dot
#   (\(\d{1,4}\)[\s\-.]?)?   optional area code in brackets + separator
#   \d{3,5}          first digit group
#   [\s\-.]          separator between groups (required)
#   \d{3,5}          second digit group
#   ([\s\-.]\d{3,4})?  optional third digit group
PHONE_PATTERN = r"\+\d{1,3}[\s\-.]?(\(\d{1,4}\)[\s\-.]?)?\d{3,5}[\s\-.]\d{3,5}([\s\-.]\d{3,4})?"


# Credit card pattern breakdown:
#   \b          word boundary so we don't grab part of a longer number
#   \d{4}       exactly 4 digits
#   [\s\-]      separator: space or hyphen
#   \d{4}       exactly 4 digits (repeated 4 times for 16 digits total)
#   \b          closing word boundary
CARD_PATTERN = r"\b\d{4}[\s\-]\d{4}[\s\-]\d{4}[\s\-]\d{4}\b"


# Currency pattern breakdown:
#   [$£€₦]       one currency symbol
#   \d{1,3}      first digit group (1 to 3 digits)
#   (,\d{3})*    zero or more thousands groups (e.g. ,000)
#   (\.\d{2})?   optional decimal part (e.g. .99)
CURRENCY_PATTERN = r"[$£€₦]\d{1,3}(,\d{3})*(\.\d{2})?"


# ══════════════════════════════════════════════════════════════
#  ALU EMAIL CLASSIFICATION
# ══════════════════════════════════════════════════════════════

def classify_email(email):
    """Sort an email into one of four ALU categories."""
    email = email.lower()
    # Check SI and alumni first — they are more specific subdomains
    # of alueducation.com, so they must come before the staff check
    if email.endswith("@si.alueducation.com"):
        return "alu_si"
    elif email.endswith("@alumni.alueducation.com"):
        return "alu_alumni"
    elif email.endswith("@alueducation.com"):
        return "alu_staff"
    else:
        return "external"


# ══════════════════════════════════════════════════════════════
#  BASIC SECURITY CHECK
# ══════════════════════════════════════════════════════════════

def looks_suspicious(value):
    """Return True if the value looks like an injection attempt."""
    bad_patterns = ["--", "OR 1=1", "<script", "DROP TABLE", "javascript:"]
    for pattern in bad_patterns:
        if pattern.lower() in value.lower():
            return True
    return False


def mask_card(card):
    """Show only the last 4 digits of a card number."""
    digits = re.sub(r"\D", "", card)   # \D = any non-digit → remove them
    return "XXXX-XXXX-XXXX-" + digits[-4:]


# ══════════════════════════════════════════════════════════════
#  EXTRACTION
# ══════════════════════════════════════════════════════════════

# --- Emails ---
all_emails = re.findall(EMAIL_PATTERN, text)
emails = {"alu_staff": [], "alu_alumni": [], "alu_si": [], "external": [], "rejected": []}

for email in set(all_emails):
    if looks_suspicious(email):
        emails["rejected"].append(email)
    else:
        category = classify_email(email)
        emails[category].append(email)

print("EMAILS FOUND:")
for category, items in emails.items():
    if items:
        print(f"  [{category}] {items}")

# --- Phone Numbers ---
# re.finditer gives us the full match, not just the captured groups
phones = {"valid": [], "rejected": []}
seen_phones = set()
for match in re.finditer(PHONE_PATTERN, text):
    phone = match.group().strip()
    if phone in seen_phones:
        continue
    seen_phones.add(phone)
    if looks_suspicious(phone):
        phones["rejected"].append(phone)
    else:
        phones["valid"].append(phone)

print("\nPHONES FOUND:")
print(f"  Valid:    {phones['valid']}")
print(f"  Rejected: {phones['rejected']}")

# --- Credit Cards ---
all_cards = re.findall(CARD_PATTERN, text)
cards = {"valid": [], "rejected": []}

for card in set(all_cards):
    if looks_suspicious(card):
        cards["rejected"].append({"masked": mask_card(card), "reason": "suspicious"})
    else:
        # Always mask card numbers — never store or print the real number
        cards["valid"].append(mask_card(card))

print("\nCREDIT CARDS FOUND (masked for safety):")
print(f"  Valid:    {cards['valid']}")
print(f"  Rejected: {cards['rejected']}")

# --- Currency ---
currency = list(set(re.findall(CURRENCY_PATTERN, text)))

# re.findall returns tuples when there are groups — we only want the full match
seen_currency = set()
currency_list = []
for match in re.finditer(CURRENCY_PATTERN, text):
    amount = match.group()
    if amount not in seen_currency:
        seen_currency.add(amount)
        currency_list.append(amount)

print(f"\nCURRENCY AMOUNTS FOUND: {currency_list}")


# ══════════════════════════════════════════════════════════════
#  SAVE OUTPUT TO JSON
# ══════════════════════════════════════════════════════════════

output = {
    "emails": emails,
    "phones": phones,
    "credit_cards": cards,
    "currency": currency_list
}

with open("output/sample-output.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\nDone! Results saved to output/sample-output.json")