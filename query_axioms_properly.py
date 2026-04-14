
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient

client = SNOMEDClient()

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

# Instead of relying on lookup() which seems to return limited property codes
# (and apparently doesn't include "Finding site" directly in this server's response format),
# I will use the ECL attribute refinement search functionality which is robust.
# If I want the finding site, I can query for it specifically.

for name, code in concepts.items():
    print(f"--- {name} ({code}) ---")
    # Finding site is 363698007
    # Let's search if this concept has a 'finding site'
    # By searching for concepts that match "code" and have attribute "363698007"
    # Actually, the simplest way is to just print the descendants or do an ECL query
    # but let's try to query finding site specifically for this concept.
    
    # ECL for this: "38341003 : 363698007 = *"
    ecl = f"{code} : 363698007 = *"
    results = client.get_ecl(ecl)
    if results:
        for r in results:
            print(f"Finding site: {r['display']}")
    else:
        # Maybe it's not a finding site (for drugs, it's something else)
        print("No finding site found (possibly a drug or different type).")

    # Let's try to see attributes for drugs (e.g. 413838009)
    # 385057009 is 'Procedure site' or similar?
    # No, let's just search for ANY attributes for this concept if we can.
    # Actually, the API I have is limited. I will just use my search tool to find descriptive axioms.
