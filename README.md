# SNOMED CT Python Client

A Python client library for querying SNOMED CT (Systematized Nomenclature of Medicine – Clinical Terms) concepts via the [CSIRO Ontoserver](https://r4.ontoserver.csiro.au/fhir) public FHIR R4 API. No authentication required.

## Overview

SNOMED CT is a comprehensive, standardized clinical terminology used worldwide in electronic health records and clinical decision support systems. This library wraps the CSIRO Ontoserver FHIR R4 endpoint to make common SNOMED CT operations easy to perform from Python.

## Features

- **Text search** — find clinical concepts by keyword, optionally scoped to a hierarchy
- **Concept lookup** — retrieve display names, synonyms, and metadata by concept ID
- **Hierarchy traversal** — get all descendants (subtypes) of any concept
- **ECL queries** — execute complex [Expression Constraint Language](https://confluence.ihtsdotools.org/display/DOCECL) expressions
- **Subtype checking** — determine if one concept is a subtype of another
- **Concept validation** — verify that a concept ID exists and is active
- **Axiom retrieval** — get defining relationships and attributes for a concept
- **Axiom search** — find concepts with a specific attribute→value relationship

## Requirements

- Python 3.12+
- `requests >= 2.28.0`

## Installation

```bash
# Clone the repository
git clone https://github.com/JAson1232/SNOMEDAGENTSKILL.git
cd SNOMEDAGENTSKILL

# Install dependencies
pip install requests
```

No build step is needed — `snomed_client.py` is a single-file library you can import directly.

## Quick Start

```python
from snomed_client import SNOMEDClient

client = SNOMEDClient()

# Search for a concept by text
results = client.search("asthma", limit=5)
for r in results:
    print(r["id"], r["display"])

# Look up a concept by ID
info = client.lookup("195967001")   # Asthma
print(info["display"])

# Get all subtypes of "Asthma"
descendants = client.get_descendants("195967001")

# Check if a concept is a subtype of another
is_sub = client.is_subtype_of("195967001", "413350009")  # Asthma < Finding?

# Validate a concept ID
valid = client.validate("195967001")
print(valid["active"])

# Get defining axioms for a concept
axioms = client.get_axioms("195967001")

# Search for concepts that have a specific attribute relationship
# e.g. concepts with "finding site" = "lung structure"
matches = client.search_by_axiom(
    attribute_id="363698007",  # Finding site
    value_id="39607008"        # Lung structure
)
```

## API Reference

### `SNOMEDClient(base_url=None)`

Creates a client instance. Defaults to the CSIRO Ontoserver FHIR R4 endpoint.

---

### `search(term, ecl=None, view="inferred", limit=10, offset=0)`

Free-text search for concepts matching `term`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `term` | `str` | Search string |
| `ecl` | `str` \| `None` | Optional ECL expression to scope results to a hierarchy |
| `view` | `str` | `"inferred"` (default) or `"stated"` |
| `limit` | `int` | Max results to return |
| `offset` | `int` | Pagination offset |

Returns a list of `{"id": ..., "display": ...}` dicts.

---

### `lookup(concept_id)`

Returns full metadata for a concept: display name, synonyms, and properties.

---

### `get_display(concept_id)`

Quick helper that returns just the display string for a concept ID.

---

### `get_descendants(concept_id, view="inferred")`

Returns all subtypes (descendants) of `concept_id` in the SNOMED hierarchy.

---

### `get_ecl(ecl_expression, view="inferred")`

Executes an arbitrary ECL expression and returns the matching concepts.

---

### `is_subtype_of(concept_id, parent_id)`

Returns `True` if `concept_id` is a subtype of `parent_id`, `False` otherwise.

---

### `validate(concept_id)`

Checks whether a concept ID exists and is active. Returns a dict with at minimum an `"active"` key.

---

### `get_axioms(concept_id, view="inferred")`

Retrieves the defining relationships (axioms) for `concept_id`, including all attribute→value pairs.

---

### `search_by_axiom(attribute_id, value_id, term=None, scope_ecl=None)`

Finds concepts that have the given attribute→value relationship. Optionally filter further by `term` (text) or `scope_ecl` (hierarchy).

## Running the Examples

```bash
python3 examples/examples.py          # Core operations demo
python3 examples/search_codes.py      # Text search examples
python3 examples/verify_axioms_final.py  # Axiom retrieval demo
```

## Project Structure

```
SNOMEDAPI/
├── snomed_client.py   # Main client library
├── SKILL.md           # Detailed usage guide with worked examples
└── examples/
    ├── requirements.txt
    ├── examples.py
    ├── search_codes.py
    ├── verify_axioms_final.py
    └── ...            # Additional example and test scripts
```

## External Service

All queries are sent to the [CSIRO Ontoserver](https://r4.ontoserver.csiro.au/fhir) public endpoint. This service is provided free of charge for non-production use; check the [CSIRO terms](https://ontoserver.csiro.au) before using it in a production system.

## License

See repository for license details.
