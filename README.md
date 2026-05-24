# ALU Regex Data Extraction & Validation

A Python program that reads a raw text file and uses regular expressions to extract and validate four types of structured data: email addresses, phone numbers, credit card numbers, and currency amounts.

---

## Project Structure

```
alu-regex-data-extraction_student/
├── input/
│   └── raw-text.txt          # The raw text the program reads from
├── src/
│   └── main.py               # The main Python program
├── output/
│   └── sample-output.json    # The results after running the program
└── README.md
```

---

## How to Run

Make sure you have Python 3 installed. No extra libraries are needed.

Open your terminal, navigate to the project folder, and run:

```bash
python src/main.py
```

The results will be printed in the terminal and saved to `output/sample-output.json`.

---

## What the Program Does

1. Reads the raw text from `input/raw-text.txt`
2. Searches through the text using regex patterns
3. Validates each match — rejecting anything that looks suspicious
4. Prints the results to the terminal
5. Saves everything into a JSON file

---

## Data Types Extracted

### 1. Email Addresses
Finds all email addresses in the text and sorts them into four categories:

| Category | Domain |
|---|---|
| `alu_staff` | `@alueducation.com` |
| `alu_alumni` | `@alumni.alueducation.com` |
| `alu_si` | `@si.alueducation.com` |
| `external` | Any other valid email |

Pattern used:
```
[a-zA-Z0-9._+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}
```

### 2. Phone Numbers
Finds international phone numbers that start with a `+` country code.

Examples matched: `+250 788 123 456`, `+1 (555) 867-5309`, `+1-800-555-0199`

Pattern used:
```
\+\d{1,3}[\s\-.]?(\(\d{1,4}\)[\s\-.]?)?\d{3,5}[\s\-.]\d{3,5}([\s\-.]\d{3,4})?
```

### 3. Credit Card Numbers
Finds 16-digit card numbers written in groups of 4, separated by spaces or hyphens.

Example matched: `4111 1111 1111 1111`

For security, card numbers are **always masked** in the output — only the last 4 digits are shown: `XXXX-XXXX-XXXX-1111`

Pattern used:
```
\b\d{4}[\s\-]\d{4}[\s\-]\d{4}[\s\-]\d{4}\b
```

### 4. Currency Amounts
Finds amounts with a currency symbol in front of them.

Symbols supported: `$` `£` `€` `₦`

Examples matched: `$1,250.00`, `£450.00`, `₦75,000.00`

Pattern used:
```
[$£€₦]\d{1,3}(,\d{3})*(\.\d{2})?
```

---

## Regex Building Blocks Used

Every pattern in this program is built from these basic regex symbols:

| Symbol | Meaning |
|---|---
| `[abc]` | One of these characters |
| `[a-z]` | Any character in this range |
| `[^abc]` | Any character except these |
| `\d` | Any digit (0–9) |
| `\D` | Any non-digit |
| `\w` | Any word character (letter, digit, underscore) |
| `\s` | Any whitespace character |
| `\b` | Word boundary |
| `+` | One or more |
| `*` | Zero or more |
| `?` | Zero or one (makes something optional) |
| `{n}` | Exactly n times |
| `{n,m}` | Between n and m times |
| `(...)` | Group |
| `(a\|b)` | a or b |
| `^` | Start of line |
| `$` | End of line |



## Security

The program does not automatically trust the input. Before accepting any match, it runs a basic check for common attack patterns:

- -- and OR 1=1 — SQL injection
- DROP TABLE — SQL injection
- <script  — JavaScript / XSS injection
- javascript:` — dangerous URL scheme

Any match that contains these patterns is moved to a `rejected` list instead of the valid results.

Credit card numbers are never stored or printed in their raw form — they are always masked before being added to any output.


## Sample Output

json
{
  "emails": {
    "alu_staff": ["k.nakamura@alueducation.com", "finance@alueducation.com"],
    "alu_alumni": ["p.adeyemi@alumni.alueducation.com"],
    "alu_si": ["billing@si.alueducation.com"],
    "external": ["john.doe@gmail.com"],
    "rejected": ["--@evil.com"]
  },
  "phones": {
    "valid": ["+250 788 123 456", "+1 (555) 867-5309"],
    "rejected": []
  },
  "credit_cards": {
    "valid": ["XXXX-XXXX-XXXX-1111"],
    "rejected": []
  },
  "currency": ["$1,250.00", "$89.99", "£450.00", "₦75,000.00"]
}
