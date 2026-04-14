
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient
import pprint

client = SNOMEDClient()

# Hypertension (38341003)
# Angina pectoris (194828000)
# Hypercholesterolemia (13644009)
# Statin drug (413838009)
# Myocardial ischemia (414029004)
# Osteoarthritis (396275006)
# Peripheral nerve block (88815003)
# Chronic kidney disease (709044004)
# Ezetimibe (408041006)
# PCSK9 inhibitor (737573001)

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

# The lookup() returned 'properties' which included 'parent' and 'child'.
# Let's see if we can find other relationships if we search specifically for ECL patterns.
# Common SNOMED attributes:
# 363698007: Finding site
# 127489000: Has active ingredient
# 246075003: Causative agent
# 246454002: Occurs after
# 363714003: Interprets
# 42752001: Due to

attributes_to_check = {
    "363698007": "Finding site",
    "127489000": "Has active ingredient",
    "246075003": "Causative agent",
    "363714003": "Interprets",
    "42752001": "Due to",
    "47429007": "Associated with"
}

for name, code in concepts.items():
    print(f"--- {name} ({code}) ---")
    for attr_code, attr_name in attributes_to_check.items():
        # Check if the concept matches: Concept : Attribute = *
        ecl = f"{code} : {attr_code} = *"
        results = client.get_ecl(ecl)
        if results:
             # Just print one to see what it is
             print(f"Has {attr_name}")
