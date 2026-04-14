
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient
import pprint

client = SNOMEDClient()

test_concepts = ["38341003", "413838009"] # Hypertension, Statin drug

for code in test_concepts:
    print(f"--- Inspecting Axioms for {code} ---")
    axioms = client.get_axioms(code)
    pprint.pprint(axioms)
