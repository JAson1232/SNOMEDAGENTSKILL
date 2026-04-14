
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient

client = SNOMEDClient()

concept = "38341003"
# The FHIR CodeSystem/$lookup operation usually returns properties.
# Maybe the server does not support returning axioms/attributes this way.
# Let's see if we can get all properties.
params = {
    "system": "http://snomed.info/sct",
    "code": concept,
    "_format": "json",
}
# The FHIR base is https://r4.ontoserver.csiro.au/fhir
# I will make a direct request to see the raw JSON
import requests
resp = requests.get("https://r4.ontoserver.csiro.au/fhir/CodeSystem/$lookup", params=params)
print(resp.json())
