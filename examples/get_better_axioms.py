
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient

client = SNOMEDClient()

# Codes identified in Exercise 1d
concepts = {
    "Hypertension": "38341003",
    "Angina pectoris": "194828000",
    "Hypercholesterolemia": "13644009",
    "Statin drug": "413838009",
    "Myocardial ischemia": "414029004",
    "Osteoarthritis": "396275006",
    "Peripheral nerve block": "88815003",
    "Chronic kidney disease": "709044004",
    "Ezetimibe": "408041006",
    "PCSK9 inhibitor": "737573001"
}

print(f"{'Concept':<25} | {'Attribute (Finding site/etc)':<30} | {'Value (Target)'}")
print("-" * 80)

for name, code in concepts.items():
    axioms = client.get_axioms(code)
    # Filter for interesting relationships (usually '363698007' is Finding Site)
    found_any = False
    for attr in axioms["attributes"]:
        # Let's see what attributes we actually have
        print(f"{name:<25} | {attr['type_code']} ({attr['type_display']}) | {attr['value_code']} ({attr['value_display']})")
        found_any = True
    if not found_any:
        print(f"{name:<25} | {'No attributes found':<30} | {'-'}")
