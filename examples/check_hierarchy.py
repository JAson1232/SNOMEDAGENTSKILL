
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient

client = SNOMEDClient()

concept_id = "38341003" # Hypertension

# Get descendants to see hierarchical difference
stated = client.get_descendants(concept_id, view="stated", limit=5)
inferred = client.get_descendants(concept_id, view="inferred", limit=5)

print("Stated descendants:")
for s in stated:
    print(f"  {s['code']}: {s['display']}")

print("\nInferred descendants:")
for i in inferred:
    print(f"  {i['code']}: {i['display']}")
