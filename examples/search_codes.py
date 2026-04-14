
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient

client = SNOMEDClient()

terms_to_search = [
    "Cholesterol", "Statin", "Ezetimibe", "PCSK9 inhibitor", "LDL", 
    "Osteoarthritis", "Knee", "Osteotomy", "Opioid", 
    "Peripheral nerve block", "Femoral nerve block", "Sciatic nerve block", "Epidural analgesia"
]

for term in terms_to_search:
    results = client.search(term, limit=5)
    print(f"Term: {term}")
    for res in results:
        print(f"  Code: {res['code']}, Display: {res['display']}")
