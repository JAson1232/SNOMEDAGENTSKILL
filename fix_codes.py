
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient

client = SNOMEDClient()

queries = [
    "Osteoarthritis",
    "Peripheral nerve block",
    "Ezetimibe",
    "PCSK9 inhibitor"
]

for q in queries:
    results = client.search(q, limit=5)
    print(f"Search results for '{q}':")
    for r in results:
        print(f"  {r['code']}: {r['display']}")
