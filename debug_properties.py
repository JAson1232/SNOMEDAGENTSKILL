
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient
import requests

client = SNOMEDClient()

concept = "38341003" # Hypertension
params = {
    "system": "http://snomed.info/sct",
    "code": concept,
    "_format": "json",
}
resp = requests.get("https://r4.ontoserver.csiro.au/fhir/CodeSystem/$lookup", params=params)
data = resp.json()

# Print all property names found in the 'property' parts
for param in data.get("parameter", []):
    if param.get("name") == "property":
        parts = {p["name"]: p for p in param.get("part", [])}
        code = parts.get("code", {}).get("valueCode", "unknown")
        print(f"Property found: {code}")
