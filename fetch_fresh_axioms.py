
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient
import json

client = SNOMEDClient()

concepts = {
    "Cardiovascular disease": "49601007",
    "HMG-CoA reductase inhibitor": "372912004",
    "Ezetimibe": "408041006",
    "PCSK9 inhibitor": "737573001",
    "Chronic kidney disease": "709044004",
    "Osteoarthritis": "396275006",
    "Angina pectoris": "194828000",
    "Myocardial ischemia": "414029004",
    "Coronary computed tomography angiography": "442655000",
    "Peripheral block anaesthesia": "88815003"
}

results = {}

for name, code in concepts.items():
    axioms = client.get_axioms(code)
    results[name] = axioms

print(json.dumps(results, indent=2))
