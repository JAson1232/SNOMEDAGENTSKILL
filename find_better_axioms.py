
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient

client = SNOMEDClient()

# Let's look for fully defined subtypes (which usually have more complete axioms)
# for the concepts identified.
concepts = {
    "Hypertension": "38341003",
    "Angina pectoris": "194828000",
    "Hypercholesterolemia": "13644009",
    "Statin drug": "413838009",
    "Myocardial ischemia": "414029004",
    "Osteoarthritis": "396275006",
    "Peripheral nerve block": "88815003",
    "Ezetimibe": "408041006",
    "PCSK9 inhibitor": "737573001"
}

for name, code in concepts.items():
    print(f"--- Searching for fully defined subtypes for {name} ({code}) ---")
    # Search for subtypes with the "sufficiently defined" flag?
    # Actually, the SNOMED API doesn't have an easy "get fully defined" filter via search.
    # I'll just look for subtypes and pick one that looks more specific/defined.
    results = client.get_descendants(code, limit=5)
    for r in results:
        print(f"  {r['code']}: {r['display']}")
