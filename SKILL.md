# SNOMED CT API Skill

This document teaches agents how to query and search SNOMED CT terminology.

## Overview

SNOMED CT (Systematized Nomenclature of Medicine – Clinical Terms) is a comprehensive clinical terminology used worldwide. This integration uses the **CSIRO Ontoserver public FHIR R4 API** — no authentication required.

**FHIR Base URL:** `https://r4.ontoserver.csiro.au/fhir`  
**SNOMED System URI:** `http://snomed.info/sct`  
**Response Format:** JSON (FHIR R4 Parameters/ValueSet resources)

> **Note:** The CSIRO public server is for non-production/research use. IHTSDO's Snowstorm server (browser.ihtsdotools.org) has been decommissioned as of 2025.

---

## Python Client

Use `snomed_client.py` in this directory. No extra setup beyond `pip install requests`.

```python
from snomed_client import SNOMEDClient

client = SNOMEDClient()
```

---

## Core Operations

### 1. Search Concepts by Text

Find SNOMED concepts matching a free-text search term.

```python
results = client.search("asthma", limit=10)
for concept in results:
    print(concept["code"], concept["display"])
# 195967001  Asthma
# 55570000   Asthma without status asthmaticus
# ...
```

Scope the search to a specific part of the hierarchy using ECL:

```python
# Search "diabetes" only within clinical findings
results = client.search("diabetes", ecl="<404684003", limit=10)
```

**Direct HTTP:**
```
GET /fhir/ValueSet/$expand?url=http://snomed.info/sct?fhir_vs&filter=asthma&count=10&_format=json
```

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `term` | Free-text search |
| `ecl` | ECL expression to scope the search |
| `view` | `"inferred"` (default) or `"stated"` — controls which relationship view is used when `ecl` is provided |
| `limit` | Max results (default 20) |
| `offset` | Pagination offset |

---

### 2. Look Up a Concept by ID

Get the display name and metadata for a known SNOMED Concept ID.

```python
info = client.lookup("195967001")
print(info["display"])      # "Asthma"
print(info["version"])      # SNOMED release version
print(info["designations"]) # All synonyms
```

**Direct HTTP:**
```
GET /fhir/CodeSystem/$lookup?system=http://snomed.info/sct&code=195967001&_format=json
```

**Response fields:**
- `code` — SNOMED concept ID
- `display` — preferred display term
- `designations` — list of `{"language", "use", "value"}` (synonyms, FSN, etc.)
- `properties` — concept properties (e.g. `inactive`, parent relationships)
- `version` — SNOMED release version string

**Quick display lookup:**
```python
term = client.get_display("22298006")  # "Myocardial infarction"
```

---

### 3. Get Descendants (Subtypes)

Get all concepts that are subtypes of a given concept at any level.

```python
descendants = client.get_descendants("195967001", limit=20)
for d in descendants:
    print(d["code"], d["display"])
# Returns all types of asthma in SNOMED
```

**Direct HTTP:**
```
GET /fhir/ValueSet/$expand?url=http://snomed.info/sct?fhir_vs=isa/195967001&count=20&_format=json
```

Use `view="stated"` to traverse only explicitly asserted IS-A relationships:
```python
stated_descendants = client.get_descendants("195967001", view="stated", limit=20)
```

---

### 4. ECL Queries (Expression Constraint Language)

ECL is the most powerful way to query SNOMED. Use `get_ecl()` for pure hierarchy/relationship queries.

```python
# All subtypes of Diabetes mellitus (inferred view — default)
results = client.get_ecl("<73211009", limit=20)

# Asthma AND all its subtypes (inferred view)
results = client.get_ecl("<<195967001", limit=50)

# All clinical findings that are NOT diabetes (inferred view)
results = client.get_ecl("<404684003 MINUS <<73211009", limit=20)

# Same query using the stated (asserted) view
results = client.get_ecl("<404684003 MINUS <<73211009", view="stated", limit=20)
# Equivalent to running: <!404684003 MINUS <<!73211009
```

**Direct HTTP:**
```
GET /fhir/ValueSet/$expand?url=http://snomed.info/sct?fhir_vs=ecl/%3C73211009&count=20&_format=json
```

**ECL Operators — inferred view (default):**
| Operator | Meaning | Example |
|----------|---------|---------|
| `<X` | All subtypes of X (not including X) | `<404684003` |
| `<<X` | X and all its subtypes | `<<195967001` |
| `>X` | All supertypes of X (not including X) | `>195967001` |
| `>>X` | X and all its supertypes | `>>195967001` |
| `X OR Y` | Union | `<64572001 OR <73211009` |
| `X AND Y` | Intersection | `<64572001 AND <73211009` |
| `X MINUS Y` | Exclusion | `<404684003 MINUS <<73211009` |

**ECL Operators — stated view (`view="stated"`):**
| Operator | Meaning |
|----------|---------|
| `<!X` | Stated subtypes of X (not including X) |
| `<<!X` | X and its stated subtypes |
| `>!X` | Stated supertypes of X (not including X) |
| `>>!X` | X and its stated supertypes |

> **Inferred vs. stated:** The inferred view (default) includes relationships derived by the SNOMED CT classifier — it is richer and is recommended for most queries. The stated view covers only relationships explicitly asserted in the source files; it is useful when you need to see precisely what was authored without inference.

**Useful top-level concept IDs for scoping ECL:**
| Concept ID | Fully Specified Name |
|------------|----------------------|
| `404684003` | Clinical finding |
| `71388002` | Procedure |
| `123037004` | Body structure |
| `410607006` | Organism |
| `105590001` | Substance |
| `373873005` | Pharmaceutical / biologic product |
| `272379006` | Event |
| `243796009` | Situation with explicit context |

---

### 5. Check Subtype Relationship

Check whether one concept is a subtype (descendant) of another.

```python
# Is "Asthma" a subtype of "Clinical finding"?
result = client.is_subtype_of("195967001", "404684003")  # True

# Is "Asthma" a subtype of "Procedure"?
result = client.is_subtype_of("195967001", "71388002")   # False
```

**Direct HTTP:**
```
GET /fhir/CodeSystem/$subsumes?system=http://snomed.info/sct&codeA=195967001&codeB=404684003&_format=json
```

**Response outcome values:**
- `"subsumed-by"` — codeA is a subtype of codeB (returns `True`)
- `"subsumes"` — codeA is a supertype of codeB
- `"equivalent"` — same concept
- `"not-subsumed"` — no relationship

---

### 6. Validate a Concept ID

Check if a concept ID exists and is active.

```python
is_valid = client.validate("195967001")   # True
is_valid = client.validate("999999999")   # False
```

**Direct HTTP:**
```
GET /fhir/CodeSystem/$validate-code?url=http://snomed.info/sct&code=195967001&_format=json
```

---

## Decision Guide: Choosing the Right Method

| Goal | Method |
|------|--------|
| Find a concept by name | `client.search("term")` |
| Confirm a concept ID and get its display name | `client.lookup("conceptId")` or `client.get_display("conceptId")` |
| Find all subtypes of a concept | `client.get_descendants("conceptId")` |
| Find only stated (asserted) subtypes | `client.get_descendants("conceptId", view="stated")` |
| Filter to a clinical domain when searching | `client.search("term", ecl="<topLevelId")` |
| Same search using stated relationships | `client.search("term", ecl="<topLevelId", view="stated")` |
| Complex hierarchy queries | `client.get_ecl("ecl expression")` |
| Complex query using stated relationships | `client.get_ecl("ecl expression", view="stated")` |
| Check if concept A is a subtype of concept B | `client.is_subtype_of("A", "B")` |
| Check if a concept ID is valid | `client.validate("conceptId")` |

---

## Pagination

All list-returning methods accept `limit` and `offset`:

```python
page1 = client.search("diabetes", limit=20, offset=0)
page2 = client.search("diabetes", limit=20, offset=20)
```

---

## Error Handling

```python
import requests

try:
    info = client.lookup("INVALID_ID")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("Concept not found")
    elif e.response.status_code == 422:
        print("Invalid request (bad ECL syntax or unknown code)")
    else:
        raise
```

HTTP status codes:
- `200` — Success
- `400` / `422` — Bad request (invalid ECL syntax, missing parameters)
- `404` — Concept/resource not found
- `500` — Server error (retry with backoff)

---

## Common Concept IDs Reference

| Concept ID | Preferred Term | Notes |
|------------|----------------|-------|
| `195967001` | Asthma | |
| `22298006` | Myocardial infarction | Heart attack |
| `44054006` | Diabetes mellitus type 2 | |
| `73211009` | Diabetes mellitus | Top-level diabetes |
| `38341003` | Hypertensive disorder | |
| `13645005` | Chronic obstructive lung disease | COPD |
| `254837009` | Malignant neoplasm of breast | |
| `363346000` | Malignant neoplastic disease | All cancers |
| `404684003` | Clinical finding | Top-level finding hierarchy |
| `71388002` | Procedure | Top-level procedure hierarchy |
| `123037004` | Body structure | Top-level body structure hierarchy |
| `105590001` | Substance | Top-level substance hierarchy |
