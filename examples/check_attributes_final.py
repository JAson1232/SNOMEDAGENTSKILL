
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

# The lookup() function returns a dict. Let me just use that to see all attributes.
# The attribute concept IDs are numeric.

for name, code in concepts.items():
    print(f"--- {name} ---")
    data = client.lookup(code)
    # The 'properties' field in the lookup result returned earlier had:
    # 'parent', 'child', 'inactive', 'sufficientlyDefined', 'effectiveTime', 'moduleId'
    # It didn't seem to have the actual role-group attributes.
    # I will try to use the `get_axioms` which I implemented.
    axioms = client.get_axioms(code)
    for attr in axioms["attributes"]:
        print(f"  {attr['type_code']} (Attribute) -> {attr['value_display']}")
